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
            credentials=self.credentials,
            heartbeat=600,  # 10 minutes heartbeat
            blocked_connection_timeout=300  # 5 minutes timeout
        )
        self.connection = None
        self.channel = None
        self._consuming = False
        self._closing = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Establish connection and channel"""
        try:
            if not self.connection or self.connection.is_closed:
                logger.info("Establishing new RabbitMQ connection to %s:%s", 
                          settings.RABBITMQ['HOST'], 
                          settings.RABBITMQ['PORT'])
                self.connection = pika.BlockingConnection(self.parameters)
                self.channel = self.connection.channel()
                
                # Enable publisher confirms
                self.channel.confirm_delivery()
                
                # Declare exchanges
                logger.info("Declaring transaction_events exchange")
                self.channel.exchange_declare(
                    exchange='transaction_events',
                    exchange_type='topic',
                    durable=True
                )
                
                # Declare queues with detailed logging
                logger.info("Declaring and binding queues")
                self.channel.queue_declare(
                    queue='transaction_status_events',
                    durable=True
                )
                self.channel.queue_declare(
                    queue='transaction_completion_events',
                    durable=True
                )
                
                # Bind queues to exchanges with logging
                logger.info("Binding transaction_status_events queue")
                self.channel.queue_bind(
                    exchange='transaction_events',
                    queue='transaction_status_events',
                    routing_key='transaction.failed'
                )
                logger.info("Binding transaction_completion_events queue")
                self.channel.queue_bind(
                    exchange='transaction_events',
                    queue='transaction_completion_events',
                    routing_key='transaction.completed'
                )
                
                # Set QoS
                self.channel.basic_qos(prefetch_count=1)
                
                logger.info("RabbitMQ connection and channel setup completed successfully")
        except Exception as e:
            logger.error("Failed to establish RabbitMQ connection: %s", str(e))
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            raise

    def close(self):
        """Close the connection"""
        try:
            self._closing = True
            if self.connection and not self.connection.is_closed:
                logger.info("Closing RabbitMQ connection")
                if self._consuming:
                    self.stop_consuming()
                self.connection.close()
        except Exception as e:
            logger.error("Error closing RabbitMQ connection: %s", str(e))
        finally:
            self._closing = False
            self.connection = None
            self.channel = None

    def stop_consuming(self):
        """Stop consuming messages"""
        if self._consuming:
            logger.info("Stopping message consumption")
            try:
                if self.channel and self.channel.is_open:
                    self.channel.stop_consuming()
                self._consuming = False
            except Exception as e:
                logger.error("Error stopping consumption: %s", str(e))

    @ensure_connection
    def publish(self, routing_key: str, message: dict) -> None:
        """
        Publish a message to RabbitMQ
        """
        try:
            logger.info("Publishing message:")
            logger.info("  Exchange: transaction_events")
            logger.info("  Routing Key: %s", routing_key)
            logger.info("  Message: %s", json.dumps(message, indent=2))
            
            self.channel.basic_publish(
                exchange='transaction_events',
                routing_key=routing_key,
                body=json.dumps(message).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info("Successfully published message")
        except Exception as e:
            logger.error("Failed to publish message: %s", str(e))
            logger.error("Connection state: %s", 
                        "OPEN" if self.connection and not self.connection.is_closed else "CLOSED")
            logger.error("Channel state: %s", 
                        "OPEN" if self.channel and not self.channel.is_closed else "CLOSED")
            raise

    def consume(self, queue_name: str, callback):
        """
        Start consuming messages from a queue
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
                
            logger.info("Starting consumption from queue: %s", queue_name)
            
            def wrapped_callback(ch, method, properties, body):
                """Wrapper around the callback to handle acknowledgments"""
                try:
                    logger.info("Received message:")
                    logger.info("  Queue: %s", queue_name)
                    logger.info("  Routing Key: %s", method.routing_key)
                    logger.info("  Message: %s", body.decode())
                    
                    # Call the actual callback
                    callback(ch, method, properties, body)
                    
                except Exception as e:
                    logger.error("Error processing message: %s", str(e))
                    # Reject the message and don't requeue
                    try:
                        if ch.is_open:
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    except Exception as nack_error:
                        logger.error("Error sending NACK: %s", str(nack_error))
            
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=wrapped_callback,
                auto_ack=False
            )
            
            self._consuming = True
            logger.info("Successfully started consuming from queue: %s", queue_name)
            
            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                logger.info("Received KeyboardInterrupt, stopping consumer")
                self.stop_consuming()
            except Exception as e:
                if "Channel is closed" not in str(e):
                    logger.error("Error during consumption: %s", str(e))
                self.stop_consuming()
                raise
                
        except Exception as e:
            logger.error("Failed to start consuming from queue %s: %s", queue_name, str(e))
            if not self._closing:
                self.close()
            raise 