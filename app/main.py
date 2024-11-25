from fastapi import FastAPI
from app.models.event import DeviceEvent
from app.services.kafka_producer import KafkaProducerService

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ingestion Service is running"}

# Kafka producer service
kafka_producer = KafkaProducerService()

@app.post("/events")
async def ingest_event(event: DeviceEvent):
    """
    Ingest device events and forward them to Kafka.
    """
    try:
        kafka_producer.send_event(event)
        return {"status": "success", "message": "Event sent to Kafka"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send event: {str(e)}"}

