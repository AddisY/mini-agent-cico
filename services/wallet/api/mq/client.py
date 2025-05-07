import json
import pika
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """
    RabbitMQ client for handling events
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
            self.channel.exchange_declare(
                exchange='transaction_events',
                exchange_type='topic',
                durable=True
            )

            # Declare queues
            self.channel.queue_declare(
                queue='wallet_agent_events',
                durable=True
            )
            self.channel.queue_declare(
                queue='wallet_transaction_events',
                durable=True
            )

            # Bind queues to exchanges
            self.channel.queue_bind(
                exchange='user_events',
                queue='wallet_agent_events',
                routing_key='agent.created'
            )
            self.channel.queue_bind(
                exchange='transaction_events',
                queue='wallet_transaction_events',
                routing_key='transaction.#'
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