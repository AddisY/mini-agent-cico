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

    @staticmethod
    def publish_wallet_credited(transaction_id: str, agent_id: str, amount: str, transaction_type: str = 'BANK_WITHDRAWAL'):
        """
        Publish a wallet.credited event
        """
        try:
            with RabbitMQClient() as client:
                message = {
                    'transaction_id': transaction_id,
                    'agent_id': agent_id,
                    'amount': amount,
                    'transaction_type': transaction_type
                }
                
                client.channel.basic_publish(
                    exchange='wallet_events',
                    routing_key='wallet.credited',
                    body=json.dumps(message).encode()
                )
                
                logger.info(f"Published wallet.credited event for transaction {transaction_id}")
                
        except Exception as e:
            logger.error(f"Error publishing wallet.credited event: {str(e)}")
            raise

    @staticmethod
    def publish_wallet_debited(transaction_id: str, agent_id: str, amount: str, transaction_type: str = 'WALLET_LOAD'):
        """
        Publish a wallet.debited event
        """
        try:
            with RabbitMQClient() as client:
                message = {
                    'transaction_id': transaction_id,
                    'agent_id': agent_id,
                    'amount': amount,
                    'transaction_type': transaction_type
                }
                
                client.channel.basic_publish(
                    exchange='wallet_events',
                    routing_key='wallet.debited',
                    body=json.dumps(message).encode()
                )
                
                logger.info(f"Published wallet.debited event for transaction {transaction_id}")
                
        except Exception as e:
            logger.error(f"Error publishing wallet.debited event: {str(e)}")
            raise

    @staticmethod
    def publish_transaction_completed(transaction_id: str, commission_amount: str, commission_status: bool = True):
        """
        Publish a transaction.completed event
        """
        try:
            with RabbitMQClient() as client:
                message = {
                    'transaction_id': transaction_id,
                    'commission_amount': commission_amount,
                    'commission_status': commission_status
                }
                
                client.channel.basic_publish(
                    exchange='transaction_events',
                    routing_key='transaction.completed',
                    body=json.dumps(message).encode()
                )
                
                logger.info(f"Published transaction.completed event for transaction {transaction_id}")
                
        except Exception as e:
            logger.error(f"Error publishing transaction.completed event: {str(e)}")
            raise 