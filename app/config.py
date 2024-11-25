import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "raw_device_data")

