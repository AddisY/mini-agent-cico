import logging
from decimal import Decimal
from django.db import transaction
from django.core.cache import cache
from .models import Transaction, TransactionStatus
from .mq.client import RabbitMQClient

logger = logging.getLogger(__name__)

class TransactionProcessor:
    """
    Handles transaction processing with atomicity and proper status updates.
    For demo purposes, all transactions are treated as successful.
    """
    
    def __init__(self):
        self.mq_client = RabbitMQClient()
        self.commission_rate = Decimal('0.01')  # 1% commission for demo

    def process_transaction(self, transaction_id: str) -> None:
        """
        Process a transaction with proper atomicity and status updates.
        """
        try:
            with transaction.atomic():
                # Get transaction
                tx = Transaction.objects.select_for_update().get(transaction_id=transaction_id)
                
                if tx.status != TransactionStatus.INITIATED:
                    logger.warning(f"Transaction {transaction_id} is not in INITIATED state")
                    return

                # Calculate commission (1% for demo)
                commission_amount = tx.amount * self.commission_rate
                
                # For demo purposes, all transactions are successful
                # In production, this is where we would:
                # 1. Call external provider APIs
                # 2. Update wallet balances
                # 3. Handle provider-specific logic
                
                # Update transaction status and commission
                tx.status = TransactionStatus.SUCCESSFUL
                tx.commission_amount = commission_amount
                tx.commission_status = True
                tx.save()

                # Clear cache
                cache_key = f"transaction_{transaction_id}"
                cache.delete(cache_key)

                # Publish success event
                try:
                    self.mq_client.publish(
                        routing_key='transaction.completed',
                        message={
                            'transaction_id': str(transaction_id),
                            'commission_amount': str(commission_amount),
                            'commission_status': True
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to publish completion event: {str(e)}")
                    # Don't fail the transaction if event publishing fails
                    # The transaction itself was successful

                logger.info(f"Successfully processed transaction {transaction_id}")

        except Transaction.DoesNotExist:
            logger.error(f"Transaction {transaction_id} not found")
            raise
        except Exception as e:
            logger.error(f"Failed to process transaction {transaction_id}: {str(e)}")
            self._handle_failure(transaction_id, str(e))
            raise

    def _handle_failure(self, transaction_id: str, error_message: str) -> None:
        """
        Handle transaction failure with proper status updates and event publishing
        """
        try:
            with transaction.atomic():
                tx = Transaction.objects.select_for_update().get(transaction_id=transaction_id)
                tx.status = TransactionStatus.FAILED
                tx.error_message = error_message
                tx.save()

                # Clear cache
                cache_key = f"transaction_{transaction_id}"
                cache.delete(cache_key)

                # Publish failure event
                try:
                    self.mq_client.publish(
                        routing_key='transaction.failed',
                        message={
                            'transaction_id': str(transaction_id),
                            'error_message': error_message
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to publish failure event: {str(e)}")
                    # Don't fail the error handling if event publishing fails

                logger.info(f"Marked transaction {transaction_id} as failed")
        except Exception as e:
            logger.error(f"Failed to handle transaction failure: {str(e)}")
            raise 