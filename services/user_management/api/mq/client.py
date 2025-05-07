import json
import pika
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """
    RabbitMQ client for publishing events
    """
    def __init__(self):
        self.credentials = pika.PlainCredentials(
            settings.RABBITMQ['USER'],
            settings.RABBITMQ['PASSWORD']
        )
        self.parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ['HOST'],
            port=settings.RABBITMQ['PORT'],
            virtual_host=settings.RABBITMQ['VIRTUAL_HOST'],
            credentials=self.credentials
        )
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection and channel"""
        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            
            # Declare exchanges
            self.channel.exchange_declare(
                exchange='user_events',
                exchange_type='topic',
                durable=True
            )

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def __enter__(self):
        """Context manager enter"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def publish_event(self, routing_key: str, data: dict):
        """
        Publish an event to RabbitMQ
        
        :param routing_key: The routing key for the message
        :param data: The message data to publish
        """
        try:
            self.connect()
            self.channel.basic_publish(
                exchange='user_events',
                routing_key=routing_key,
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Published event: {routing_key} - {data}")
        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}")
            raise 