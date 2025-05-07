import pika
import json
import logging
from django.conf import settings
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def ensure_connection(func: Callable) -> Callable:
    """
    Decorator to ensure RabbitMQ connection is established before executing a function
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        if not self.connection or self.connection.is_closed:
            self.connect()
        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()
        return func(self, *args, **kwargs)
    return wrapper

class RabbitMQClient:
    """
    RabbitMQ client for transaction service
    """
    def __init__(self):
        self.credentials = pika.PlainCredentials(
            settings.RABBITMQ['USER'],
            settings.RABBITMQ['PASSWORD']
        )
        self.parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ['HOST'],
            port=int(settings.RABBITMQ['PORT']),
            virtual_host=settings.RABBITMQ['VIRTUAL_HOST'],
            credentials=self.credentials
        )
        self.connection = None
        self.channel = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Establish connection and channel"""
        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            
            # Declare exchanges
            self.channel.exchange_declare(
                exchange='transaction_events',
                exchange_type='topic',
                durable=True
            )
            
            # Declare queues
            self.channel.queue_declare(
                queue='transaction_status_events',
                durable=True
            )
            self.channel.queue_declare(
                queue='transaction_completion_events',
                durable=True
            )
            
            # Bind queues to exchanges
            self.channel.queue_bind(
                exchange='transaction_events',
                queue='transaction_status_events',
                routing_key='transaction.failed'
            )
            self.channel.queue_bind(
                exchange='transaction_events',
                queue='transaction_completion_events',
                routing_key='transaction.completed'
            )

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def publish(self, routing_key: str, message: dict):
        """
        Publish a message to RabbitMQ
        """
        try:
            self.connect()
            self.channel.basic_publish(
                exchange='transaction_events',
                routing_key=routing_key,
                body=json.dumps(message).encode()
            )
            logger.info(f"Published message to {routing_key}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise

    def consume(self, queue_name: str, callback):
        """
        Start consuming messages from a queue
        """
        self.connect()
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        logger.info(f"Started consuming from queue: {queue_name}")
        self.channel.start_consuming() 