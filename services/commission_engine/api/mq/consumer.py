import os
import django
import logging
from .client import RabbitMQClient
from .handlers import EventHandler

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commission_engine.settings')
django.setup()

logger = logging.getLogger(__name__)

class EventConsumer:
    def __init__(self):
        logger.info("Initializing commission engine consumer")
        self.client = RabbitMQClient()
        self.handler = EventHandler()
        self.setup_queues()

    def setup_queues(self):
        """Declare queues and set up bindings"""
        try:
            # Declare exchanges
            exchanges = {
                'user_events': ['agent.created'],
                'wallet_events': ['wallet.credited', 'wallet.debited'],
                'commission_events': []  # We publish to this but don't consume from it
            }
            
            for exchange, _ in exchanges.items():
                self.client.channel.exchange_declare(
                    exchange=exchange,
                    exchange_type='topic',
                    durable=True
                )
            
            # Declare queues and bind them
            for exchange, routing_keys in exchanges.items():
                for key in routing_keys:
                    queue_name = key
                    self.client.channel.queue_declare(queue=queue_name, durable=True)
                    self.client.channel.queue_bind(
                        exchange=exchange,
                        queue=queue_name,
                        routing_key=key
                    )
                    
                    # Set up consumer for this queue
                    self.client.channel.basic_consume(
                        queue=queue_name,
                        on_message_callback=self._create_callback(key),
                        auto_ack=False
                    )
            
            # Set prefetch count to ensure fair dispatch
            self.client.channel.basic_qos(prefetch_count=1)
            
            logger.info("Successfully set up exchanges and queues")
            
        except Exception as e:
            logger.error(f"Failed to set up queues: {str(e)}")
            raise

    def _create_callback(self, routing_key):
        """Create a callback function for a specific routing key"""
        def callback(ch, method, properties, body):
            try:
                if routing_key == 'agent.created':
                    self.handler.handle_agent_created(ch, method, properties, body)
                elif routing_key in ['wallet.credited', 'wallet.debited']:
                    self.handler.handle_wallet_event(ch, method, properties, body)
                else:
                    logger.warning(f"No handler for routing key: {routing_key}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message on {routing_key}: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return callback

    def start(self):
        """Start consuming messages"""
        try:
            logger.info("Commission engine consumer started")
            self.client.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}")
            self.stop()
            raise

    def stop(self):
        """Stop consuming messages and close connections"""
        try:
            if self.client.channel:
                self.client.channel.stop_consuming()
            self.handler.close()
            self.client.close()
            logger.info("Consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping consumer: {str(e)}")
            raise

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    consumer = EventConsumer()
    try:
        consumer.start()
    except Exception as e:
        logger.error(f"Failed to start consumer: {str(e)}")
        logger.exception("Full traceback:")
        consumer.stop() 