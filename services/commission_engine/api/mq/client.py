import pika
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ['USER'],
                settings.RABBITMQ['PASSWORD']
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ['HOST'],
                port=settings.RABBITMQ['PORT'],
                virtual_host=settings.RABBITMQ['VIRTUAL_HOST'],
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def ensure_connection(self):
        if not self.connection or self.connection.is_closed:
            self.connect() 