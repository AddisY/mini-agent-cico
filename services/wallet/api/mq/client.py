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
        self.connection = None
        self.channel = None
        self.credentials = pika.PlainCredentials('guest', 'guest')
        self.parameters = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=self.credentials
        )
        self._consuming = False
        self._closing = False

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            if not self.connection or self.connection.is_closed:
                self.connection = pika.BlockingConnection(self.parameters)
                logger.info("Connected to RabbitMQ")
            
            if not self.channel or self.channel.is_closed:
                self.channel = self.connection.channel()
                logger.info("Created RabbitMQ channel")
                
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def close(self):
        """Close the connection"""
        try:
            self._closing = True
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {str(e)}")
            raise

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

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