import json
import logging
from decimal import Decimal
from django.core.cache import cache
from django.conf import settings
from django.db import IntegrityError
from ..models import CommissionRate, CommissionTransaction, TransactionType
from .publisher import EventPublisher

logger = logging.getLogger(__name__)

class EventHandler:
    def __init__(self):
        self.publisher = EventPublisher()

    def handle_agent_created(self, ch, method, properties, body):
        try:
            # Log the raw event data for debugging
            logger.info(f"Received agent.created event. Raw data: {body}")
            
            # Parse JSON and validate required fields
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from agent.created event: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Requeue for retry
                return
                
            agent_id = data.get('agent_id')
            if not agent_id:
                logger.error("Missing required field 'agent_id' in agent.created event")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Don't requeue invalid messages
                return
            
            logger.info(f"Processing agent.created event for agent_id: {agent_id}")
            
            try:
                # Try to get existing commission rate
                commission_rate = CommissionRate.objects.get(agent_id=agent_id)
                logger.info(f"Commission rates already exist for agent {agent_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            except CommissionRate.DoesNotExist:
                # Create default commission rates for the new agent
                try:
                    commission_rate = CommissionRate.objects.create(
                        agent_id=agent_id,
                        wallet_load_rate=Decimal('1.50'),
                        bank_deposit_rate=Decimal('1.00'),
                        bank_withdrawal_rate=Decimal('1.25')
                    )
                    logger.info(f"Successfully created commission rates for agent {agent_id}")
                    
                    # Cache the commission rate
                    cache_key = f'commission_rate_{agent_id}'
                    cache.set(cache_key, commission_rate, timeout=settings.CACHE_TTL)
                    
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except IntegrityError as e:
                    # If we get a race condition and another process created the rates
                    logger.info(f"Commission rates already exist for agent {agent_id} (race condition)")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Failed to create commission rates for agent {agent_id}: {str(e)}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Requeue for retry
            
        except Exception as e:
            logger.error(f"Unexpected error processing agent.created event: {str(e)}")
            logger.exception("Full traceback:")  # Log the full stack trace
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Requeue for retry

    def handle_wallet_event(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            agent_id = data.get('agent_id')
            transaction_id = data.get('transaction_id')
            amount = Decimal(str(data.get('amount', 0)))
            event_type = method.routing_key
            
            logger.info(f"Processing wallet event: type={event_type}, agent={agent_id}, transaction={transaction_id}, amount={amount}")
            
            # Get commission rate from cache or database
            cache_key = f'commission_rate_{agent_id}'
            commission_rate = cache.get(cache_key)
            
            if not commission_rate:
                try:
                    commission_rate = CommissionRate.objects.get(agent_id=agent_id)
                    cache.set(cache_key, commission_rate, timeout=settings.CACHE_TTL)
                    logger.info(f"Retrieved commission rate from database for agent {agent_id}")
                except CommissionRate.DoesNotExist:
                    logger.error(f"No commission rate found for agent {agent_id}")
                    self.publisher.publish_event('commission.skipped', {
                        'transaction_id': transaction_id,
                        'agent_id': agent_id,
                        'reason': 'commission_rate_not_found'
                    })
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
            
            # Check eligibility
            if not commission_rate.is_eligible:
                logger.info(f"Agent {agent_id} is not eligible for commission")
                self.publisher.publish_event('commission.skipped', {
                    'transaction_id': transaction_id,
                    'agent_id': agent_id,
                    'reason': 'agent_not_eligible'
                })
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Determine transaction type based on event
            event_transaction_type = data.get('transaction_type')
            logger.info(f"Processing transaction type from event: {event_transaction_type}")
            
            if not event_transaction_type:
                logger.error(f"Missing required transaction_type in event data for transaction {transaction_id}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
                
            try:
                # Convert string transaction type to enum
                transaction_type = TransactionType[event_transaction_type]
                logger.info(f"Validated transaction type: {transaction_type} (enum value: {transaction_type.value})")
            except (KeyError, ValueError) as e:
                logger.error(f"Invalid transaction type '{event_transaction_type}': {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            
            # Calculate commission
            rate = commission_rate.get_rate_for_transaction_type(transaction_type)
            commission_amount = (amount * rate) / Decimal('100')
            
            logger.info(
                f"Calculated commission for transaction {transaction_id}: "
                f"type={transaction_type.value}, rate={rate}%, amount={commission_amount}"
            )
            
            try:
                # Create commission transaction record
                CommissionTransaction.objects.create(
                    transaction_id=transaction_id,
                    agent_id=agent_id,
                    transaction_type=transaction_type,
                    transaction_amount=amount,
                    commission_rate=rate,
                    commission_amount=commission_amount
                )
                
                # Publish commission recorded event
                self.publisher.publish_event('commission.recorded', {
                    'transaction_id': transaction_id,
                    'agent_id': agent_id,
                    'transaction_type': transaction_type.name,
                    'commission_rate': str(rate),
                    'commission_amount': str(commission_amount)
                })
                
                logger.info(f"Successfully recorded commission for transaction {transaction_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except IntegrityError:
                logger.info(f"Commission already recorded for transaction {transaction_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Failed to record commission: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error(f"Failed to process wallet event: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def close(self):
        self.publisher.close() 