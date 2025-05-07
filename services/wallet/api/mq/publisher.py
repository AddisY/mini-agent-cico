import json
import logging
from .client import RabbitMQClient

logger = logging.getLogger(__name__)

class EventPublisher:
    """
    Publishes events to RabbitMQ
    """
    
    @staticmethod
    def publish_transaction_failed(transaction_id: str, agent_id: str, reason: str):
        """
        Publish a transaction.failed event
        """
        try:
            with RabbitMQClient() as client:
                message = {
                    'transaction_id': transaction_id,
                    'agent_id': agent_id,
                    'status': 'FAILED',
                    'reason': reason
                }
                
                client.channel.basic_publish(
                    exchange='transaction_events',
                    routing_key='transaction.failed',
                    body=json.dumps(message).encode()
                )
                
                logger.info(f"Published transaction.failed event for transaction {transaction_id}")
                
        except Exception as e:
            logger.error(f"Error publishing transaction.failed event: {str(e)}")
            raise 