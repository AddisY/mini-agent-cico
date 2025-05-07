import json
import logging
import uuid
from typing import Any, Dict
from django.core.cache import cache
from ..models import Transaction, TransactionStatus
from .client import RabbitMQClient
from ..processors import TransactionProcessor
from django.db import transaction

logger = logging.getLogger(__name__)

class TransactionEventHandler:
    def __init__(self):
        self.mq_client = RabbitMQClient()
        self.max_retries = 3
        self.retry_delay = 5000  # milliseconds
        self.processor = TransactionProcessor()

    def publish_transaction_initiated(self, transaction: Transaction) -> None:
        """
        Publish transaction initiated event
        """
        message = {
            'transaction_id': str(transaction.transaction_id),
            'transaction_type': transaction.transaction_type.name,
            'amount': str(transaction.amount),
            'agent_id': str(transaction.agent_id),
            'customer_identifier': transaction.customer_identifier,
            'provider': transaction.get_provider_display()
        }
        
        try:
            self.mq_client.publish(
                routing_key='transaction.initiated',
                message=message
            )
        except Exception as e:
            logger.error(f"Failed to publish transaction initiated event: {str(e)}")
            self._handle_publish_failure(transaction)

    def handle_transaction_initiated(self, ch: Any, method: Any, properties: Any, body: bytes) -> None:
        """
        Handle transaction initiated event
        """
        try:
            message = json.loads(body)
            transaction_id = message['transaction_id']
            
            # Process the transaction
            self.processor.process_transaction(transaction_id)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            logger.info(f"Successfully processed transaction initiated event for {transaction_id}")
        except Exception as e:
            logger.error(f"Error processing transaction initiated event: {str(e)}")
            self._handle_event_failure(ch, method, properties, body)

    def handle_transaction_completed(self, ch: Any, method: Any, properties: Any, body: bytes) -> None:
        """
        Handle transaction completed event
        """
        try:
            message = json.loads(body)
            transaction_id = uuid.UUID(message['transaction_id'])
            commission_amount = message.get('commission_amount', '0.00')
            commission_status = message.get('commission_status', False)

            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.status = TransactionStatus.SUCCESSFUL
            transaction.commission_amount = commission_amount
            transaction.commission_status = commission_status
            transaction.save()

            # Clear cache
            cache_key = f"transaction_{transaction_id}"
            cache.delete(cache_key)

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            logger.info(f"Successfully processed transaction completed event for {transaction_id}")
        except Transaction.DoesNotExist:
            logger.error(f"Transaction {message.get('transaction_id')} not found")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing transaction completed event: {str(e)}")
            self._handle_event_failure(ch, method, properties, body)

    def handle_transaction_failed(self, ch: Any, method: Any, properties: Any, body: bytes) -> None:
        """
        Handle transaction failed event
        """
        try:
            message = json.loads(body)
            transaction_id = uuid.UUID(message['transaction_id'])
            error_message = message.get('error_message', 'Unknown error')

            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.status = TransactionStatus.FAILED
            transaction.error_message = error_message
            transaction.save()

            # Clear cache
            cache_key = f"transaction_{transaction_id}"
            cache.delete(cache_key)

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            logger.info(f"Successfully processed transaction failed event for {transaction_id}")
        except Transaction.DoesNotExist:
            logger.error(f"Transaction {message.get('transaction_id')} not found")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing transaction failed event: {str(e)}")
            self._handle_event_failure(ch, method, properties, body)

    def _handle_publish_failure(self, transaction: Transaction) -> None:
        """
        Handle failure to publish event
        """
        retry_count = cache.get(f"retry_publish_{transaction.transaction_id}", 0)
        
        if retry_count < self.max_retries:
            cache.set(
                f"retry_publish_{transaction.transaction_id}",
                retry_count + 1,
                timeout=self.retry_delay
            )
            # In a real implementation, we would use Celery or similar to retry
            # For now, we'll just log it
            logger.info(f"Scheduled retry {retry_count + 1} for transaction {transaction.transaction_id}")
        else:
            transaction.status = TransactionStatus.FAILED
            transaction.error_message = "Failed to publish transaction event"
            transaction.save()
            logger.error(f"Max retries reached for publishing transaction {transaction.transaction_id}")

    def _handle_event_failure(self, ch: Any, method: Any, properties: Any, body: bytes) -> None:
        """
        Handle failure to process event
        """
        try:
            message = json.loads(body)
            retry_count = int(properties.headers.get('x-retry-count', 0))
            
            if retry_count < self.max_retries:
                # Republish with incremented retry count
                properties.headers['x-retry-count'] = retry_count + 1
                ch.basic_publish(
                    exchange=properties.exchange,
                    routing_key=method.routing_key,
                    body=body,
                    properties=properties
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Retrying event processing, attempt {retry_count + 1}")
            else:
                # Max retries reached, dead-letter the message
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                logger.error("Max retries reached for event processing")
        except Exception as e:
            logger.error(f"Error handling event failure: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @staticmethod
    def handle_transaction_failed(ch, method, properties, body):
        """
        Handle transaction.failed event
        Updates transaction status to failed with error message
        """
        try:
            data = json.loads(body)
            logger.info(f"Received transaction.failed event: {data}")
            
            transaction_id = data.get('transaction_id')
            error_message = data.get('reason')
            
            if not transaction_id:
                logger.error("No transaction_id in message")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            try:
                with transaction.atomic():
                    tx = Transaction.objects.select_for_update().get(
                        transaction_id=transaction_id
                    )
                    
                    # Update transaction status
                    tx.status = TransactionStatus.FAILED
                    tx.error_message = error_message
                    tx.save()
                    
                    # Clear cache
                    cache_key = f"transaction_{transaction_id}"
                    cache.delete(cache_key)
                    
                    logger.info(f"Updated transaction {transaction_id} status to FAILED")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
            except Transaction.DoesNotExist:
                logger.error(f"Transaction {transaction_id} not found")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            logger.error(f"Error handling transaction.failed event: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @staticmethod
    def handle_transaction_completed(ch, method, properties, body):
        """
        Handle transaction.completed event
        Updates transaction status to successful
        """
        try:
            data = json.loads(body)
            logger.info(f"Received transaction.completed event: {data}")
            
            transaction_id = data.get('transaction_id')
            commission_amount = data.get('commission_amount')
            commission_status = data.get('commission_status', False)
            
            if not transaction_id:
                logger.error("No transaction_id in message")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            try:
                with transaction.atomic():
                    tx = Transaction.objects.select_for_update().get(
                        transaction_id=transaction_id
                    )
                    
                    # Update transaction status and commission info
                    tx.status = TransactionStatus.SUCCESSFUL
                    if commission_amount:
                        tx.commission_amount = commission_amount
                        tx.commission_status = commission_status
                    tx.save()
                    
                    # Clear cache
                    cache_key = f"transaction_{transaction_id}"
                    cache.delete(cache_key)
                    
                    logger.info(f"Updated transaction {transaction_id} status to SUCCESSFUL")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
            except Transaction.DoesNotExist:
                logger.error(f"Transaction {transaction_id} not found")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            logger.error(f"Error handling transaction.completed event: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) 