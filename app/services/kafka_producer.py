from confluent_kafka import Producer
from app.config import KAFKA_BROKER, KAFKA_TOPIC
from utils.logger import get_logger

logger = get_logger(__name__)

class KafkaProducerService:
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': KAFKA_BROKER})

    def send_event(self, event):
        """
        Send an event to Kafka.
        """
        try:
            self.producer.produce(
                KAFKA_TOPIC,
                key=event.device_id,
                value=event.json(),
                callback=self.delivery_report
            )
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to send event: {str(e)}")
            raise

    @staticmethod
    def delivery_report(err, msg):
        """
        Kafka delivery callback.
        """
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
