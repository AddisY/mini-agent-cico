import json
import logging
from .client import RabbitMQClient
import pika

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self):
        self.client = RabbitMQClient()

    def publish_event(self, event_type: str, data: dict):
        try:
            self.client.ensure_connection()
            self.client.channel.basic_publish(
                exchange='commission_events',
                routing_key=event_type,
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Published event {event_type} with data: {data}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {str(e)}")
            raise

    def close(self):
        self.client.close() 