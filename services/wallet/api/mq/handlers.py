import json
import logging
from decimal import Decimal
from django.db import transaction
from ..models import Wallet
from .publisher import EventPublisher

logger = logging.getLogger(__name__)

class EventHandler:
    """
    Handles RabbitMQ events for wallet service
    """
    
    @staticmethod
    def handle_agent_created(ch, method, properties, body):
        """
        Handle agent.created event
        Creates a new wallet for the agent
        """
        try:
            data = json.loads(body)
            logger.info(f"Received agent.created event with data: {data}")
            
            agent_id = data.get('agent_id')
            logger.info(f"Extracted agent_id: {agent_id}, type: {type(agent_id)}")
            
            if not agent_id:
                logger.error("No agent_id in message")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            try:
                # Create wallet if it doesn't exist
                wallet, created = Wallet.objects.get_or_create(agent_id=agent_id)
                
                if created:
                    logger.info(f"Created wallet for agent {agent_id}")
                else:
                    logger.info(f"Wallet already exists for agent {agent_id}")
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error creating wallet: {str(e)}, type: {type(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Error handling agent.created event: {str(e)}, type: {type(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @staticmethod
    def handle_transaction_event(ch, method, properties, body):
        """
        Handle transaction events
        Updates wallet balance based on transaction status
        """
        try:
            data = json.loads(body)
            transaction_id = data.get('transaction_id')
            agent_id = data.get('agent_id')
            amount = Decimal(str(data.get('amount', '0')))
            transaction_type = data.get('transaction_type')
            status = data.get('status')
            
            logger.info(f"Received transaction event: {data}")

            if not all([transaction_id, agent_id, amount, status]):
                logger.error("Missing required fields in transaction event")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            is_credit = transaction_type in ['WALLET_LOAD', 'BANK_DEPOSIT']

            try:
                with transaction.atomic():
                    wallet = Wallet.objects.select_for_update().get(agent_id=agent_id)
                    
                    # Handle different transaction statuses
                    if status == 'INITIATED' and not is_credit:
                        # For debit transactions, we need to check the balance
                        if wallet.balance < amount:
                            logger.error(f"Insufficient balance for transaction {transaction_id}")
                            # Publish transaction.failed event
                            EventPublisher.publish_transaction_failed(
                                transaction_id=transaction_id,
                                agent_id=agent_id,
                                reason=f"Insufficient balance. Required: {amount}, Available: {wallet.balance}"
                            )
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            return
                        # If sufficient balance, we don't need to do anything yet
                        logger.info(f"Sufficient balance for transaction {transaction_id}")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                        
                    elif status == 'SUCCESSFUL':
                        # Update balance for successful transactions
                        wallet.update_balance(amount, is_credit)
                        logger.info(f"Updated balance for wallet {wallet.id}, transaction {transaction_id}")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                        
                    elif status == 'FAILED':
                        # No balance update needed for failed transactions
                        logger.info(f"Transaction {transaction_id} failed, no balance update needed")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                    
                    else:
                        logger.warning(f"Unhandled transaction status: {status}")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                
            except Wallet.DoesNotExist:
                logger.error(f"No wallet found for agent {agent_id}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except ValueError as e:
                logger.error(f"Balance update failed: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            logger.error(f"Error handling transaction event: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) 