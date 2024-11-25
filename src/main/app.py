from fastapi import FastAPI
from pydantic import BaseModel, Field
import time
from confluent_kafka import Producer
import logging
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ingestion Service is running"}

# EventPayload model
class EventPayload(BaseModel):
    cpu_usage: int = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: int = Field(..., ge=0, le=100, description="Memory usage percentage")
    battery_status: str = Field(..., pattern="^(charging|discharging)$", description="Battery status")
    temperature: int = Field(..., description="Device temperature in Celsius")

# DeviceEvent model
class DeviceEvent(BaseModel):
    device_id: str
    event_type: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    payload: EventPayload

# Logger setup
def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        file_handler = logging.FileHandler("app.log")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger(__name__)

# Hardcoded Kafka configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "raw_device_data"

# Kafka producer service
class KafkaProducerService:
    def __init__(self):
        try:
            self.producer = Producer({'bootstrap.servers': KAFKA_BROKER})
            logger.info(f"Connected to Kafka broker at {KAFKA_BROKER}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            raise

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Delivery failed for record {msg.key()}: {err}")
        else:
            logger.info(f"Record {msg.key()} successfully delivered to {msg.topic()} partition {msg.partition()}")

    def send_event(self, event):
        try:
            self.producer.produce(
                KAFKA_TOPIC,
                key=event.device_id,
                value=event.json(),
                callback=self.delivery_report
            )
            self.producer.poll(0)  # Non-blocking flush
        except Exception as e:
            logger.error(f"Failed to send event: {str(e)}")
            raise

# Kafka producer instance
kafka_producer = KafkaProducerService()

@app.on_event("startup")
async def startup_event():
    """
    Runs on application startup to ensure Kafka connectivity.
    """
    try:
        # Test Kafka connectivity by producing a test message
        kafka_producer.producer.produce(
            KAFKA_TOPIC,
            key="test",
            value='{"test_message": "Kafka connection successful"}'
        )
        kafka_producer.producer.flush()
        logger.info(f"Successfully connected to Kafka and ready to produce to topic '{KAFKA_TOPIC}'")
    except Exception as e:
        logger.error(f"Failed to verify Kafka connection on startup: {str(e)}")
        raise RuntimeError("Failed to connect to Kafka")

@app.post("/events")
async def ingest_event(event: DeviceEvent):
    """
    Ingest device events and forward them to Kafka.
    """
    try:
        kafka_producer.send_event(event)
        return {"status": "success", "message": "Event sent to Kafka"}
    except Exception as e:
        logger.error(f"Error ingesting event: {str(e)}")
        return {"status": "error", "message": f"Failed to send event: {str(e)}"}
