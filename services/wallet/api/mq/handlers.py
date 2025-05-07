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
                # Try to get existing wallet first
                try:
                    wallet = Wallet.objects.get(agent_id=agent_id)
                    logger.info(f"Wallet already exists for agent {agent_id}")
                except Wallet.DoesNotExist:
                    # Create new wallet with initial balance
                    wallet = Wallet.objects.create(
                        agent_id=agent_id,
                        balance=Decimal('10000.00'),  # Initial balance of 10,000
                        is_active=True
                    )
                    logger.info(f"Created new wallet for agent {agent_id} with initial balance")
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error creating wallet: {str(e)}, type: {type(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"Error handling agent.created event: {str(e)}, type: {type(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @staticmethod
    def handle_transaction_event(ch, method, properties, body):
        """
        Handle transaction events
        Updates wallet balance based on transaction status and type
        """
        try:
            data = json.loads(body)
            transaction_id = data.get('transaction_id')
            agent_id = data.get('agent_id')
            amount = Decimal(str(data.get('amount', '0')))
            transaction_type = data.get('transaction_type')
            status = data.get('status')
            
            logger.info(f"Received transaction event with data: {data}")
            logger.info(f"Processing transaction: ID={transaction_id}, Type={transaction_type}, Status={status}, Amount={amount}")

            if not all([transaction_id, agent_id, amount, status]):
                logger.error("Missing required fields in transaction event")
                logger.error(f"Required fields: transaction_id={transaction_id}, agent_id={agent_id}, amount={amount}, status={status}")
                # Don't requeue messages with missing fields
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                return

            # For wallet load and bank deposit, we debit the agent's float wallet
            # For bank withdrawal, we credit the agent's float wallet
            is_credit = transaction_type == 'BANK_WITHDRAWAL'  # Compare with normalized format
            logger.info(f"Transaction type check: received_type='{transaction_type}', is_bank_withdrawal={transaction_type == 'BANK_WITHDRAWAL'}")
            logger.info(f"Transaction will be processed as a {'credit' if is_credit else 'debit'} operation")

            try:
                with transaction.atomic():
                    logger.info(f"Looking up wallet for agent_id: {agent_id}")
                    wallet = Wallet.objects.select_for_update().get(agent_id=agent_id)
                    logger.info(f"Found wallet with current balance: {wallet.balance}")
                    
                    if status == 'INITIATED':
                        logger.info("Processing INITIATED transaction")
                        # For debit transactions, we need to check the balance
                        if not is_credit and wallet.balance < amount:
                            logger.error(f"Insufficient balance. Required: {amount}, Available: {wallet.balance}")
                            EventPublisher.publish_transaction_failed(
                                transaction_id=transaction_id,
                                agent_id=agent_id,
                                reason=f"Insufficient balance. Required: {amount}, Available: {wallet.balance}"
                            )
                            # Acknowledge the message since we've handled the insufficient balance case
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            return
                        
                        # If sufficient balance, update it immediately for float transactions
                        try:
                            logger.info(f"Updating wallet balance: Current={wallet.balance}, Amount={amount}, Operation={'credit' if is_credit else 'debit'}")
                            old_balance = wallet.balance
                            wallet.update_balance(amount, is_credit)
                            logger.info(f"Balance updated successfully: Old={old_balance}, New={wallet.balance}")
                            
                            # Publish appropriate event based on credit/debit
                            if is_credit:
                                logger.info("Publishing wallet.credited event")
                                EventPublisher.publish_wallet_credited(
                                    transaction_id=transaction_id,
                                    agent_id=agent_id,
                                    amount=str(amount),
                                    transaction_type=transaction_type
                                )
                            else:
                                logger.info("Publishing wallet.debited event")
                                EventPublisher.publish_wallet_debited(
                                    transaction_id=transaction_id,
                                    agent_id=agent_id,
                                    amount=str(amount),
                                    transaction_type=transaction_type
                                )
                            
                            # Acknowledge successful processing
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            return
                            
                        except ValueError as e:
                            logger.error(f"Balance update failed with error: {str(e)}")
                            EventPublisher.publish_transaction_failed(
                                transaction_id=transaction_id,
                                agent_id=agent_id,
                                reason=str(e)
                            )
                            # Acknowledge the message since we've handled the error case
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                        
                    elif status == 'SUCCESSFUL':
                        logger.info(f"Transaction {transaction_id} already successful, no action needed")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                        
                    elif status == 'FAILED':
                        logger.info(f"Transaction {transaction_id} failed, no balance update needed")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                    
                    else:
                        logger.warning(f"Unhandled transaction status: {status}")
                        # Don't requeue messages with unknown status
                        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                        return
                
            except Wallet.DoesNotExist:
                logger.error(f"No wallet found for agent {agent_id}")
                # Don't requeue if wallet doesn't exist
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            except ValueError as e:
                logger.error(f"Balance update failed: {str(e)}")
                # Don't requeue on validation errors
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            logger.error(f"Error handling transaction event: {str(e)}")
            # Don't requeue on general errors
            try:
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as ack_error:
                logger.error(f"Error sending reject: {str(ack_error)}") 

    @staticmethod
    def handle_commission_recorded(ch, method, properties, body):
        """
        Handle commission.recorded event
        Applies commission to agent's wallet and emits transaction.completed
        """
        try:
            data = json.loads(body)
            logger.info(f"Received commission.recorded event: {data}")
            
            transaction_id = data.get('transaction_id')
            agent_id = data.get('agent_id')
            commission_amount = Decimal(str(data.get('commission_amount', '0')))
            transaction_type = data.get('transaction_type')
            
            if not all([transaction_id, agent_id, commission_amount]):
                logger.error("Missing required fields in commission.recorded event")
                logger.error(f"Required fields: transaction_id={transaction_id}, agent_id={agent_id}, commission_amount={commission_amount}")
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                return

            try:
                with transaction.atomic():
                    # Get agent's wallet
                    wallet = Wallet.objects.select_for_update().get(agent_id=agent_id)
                    
                    # Deduct commission from wallet
                    old_balance = wallet.balance
                    wallet.update_balance(commission_amount, is_credit=False)  # Always debit commission
                    logger.info(f"Applied commission deduction: Old balance={old_balance}, New balance={wallet.balance}, Commission amount={commission_amount}")
                    
                    # Publish transaction.completed event
                    EventPublisher.publish_transaction_completed(
                        transaction_id=transaction_id,
                        commission_amount=str(commission_amount),
                        commission_status=True
                    )
                    
                    logger.info(f"Successfully processed commission for transaction {transaction_id}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
            except Wallet.DoesNotExist:
                logger.error(f"No wallet found for agent {agent_id}")
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            except ValueError as e:
                logger.error(f"Failed to apply commission: {str(e)}")
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            logger.error(f"Error handling commission.recorded event: {str(e)}")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False) 