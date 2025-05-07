import pika
import json
import logging
import uuid
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_rabbitmq():
    """Establish connection to RabbitMQ"""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declare exchange
    channel.exchange_declare(
        exchange='wallet_events',
        exchange_type='topic',
        durable=True
    )
    
    return connection, channel

def publish_wallet_event(channel, event_type, agent_id, amount, operation_type=None):
    """Publish a wallet event"""
    transaction_id = str(uuid.uuid4())
    
    # Determine transaction type based on event type and operation
    if event_type == 'wallet.credited':
        transaction_type = 'BANK_WITHDRAWAL'
    else:  # wallet.debited
        transaction_type = 'BANK_DEPOSIT' if operation_type == 'BANK_DEPOSIT' else 'WALLET_LOAD'
    
    message = {
        'transaction_id': transaction_id,
        'agent_id': agent_id,
        'amount': str(amount),
        'transaction_type': transaction_type  # Add transaction type
    }
    
    if operation_type:
        message['operation_type'] = operation_type
    
    channel.basic_publish(
        exchange='wallet_events',
        routing_key=event_type,
        body=json.dumps(message)
    )
    
    logger.info(f"Published {event_type} event: {message}")
    return transaction_id

def main():
    # Test data
    agent_id = "AG1F12F9C1"
    
    try:
        connection, channel = connect_rabbitmq()
        
        # Test Case 1: Bank Withdrawal (wallet.credited)
        amount = Decimal('1000.00')
        logger.info("\nTesting bank withdrawal (1.25% commission)...")
        publish_wallet_event(channel, 'wallet.credited', agent_id, amount)
        input("Press Enter to continue...")

        # Test Case 2: Wallet Load (wallet.debited)
        amount = Decimal('500.00')
        logger.info("\nTesting wallet load (1.50% commission)...")
        publish_wallet_event(channel, 'wallet.debited', agent_id, amount, 'WALLET_LOAD')
        input("Press Enter to continue...")

        # Test Case 3: Bank Deposit (wallet.debited)
        amount = Decimal('750.00')
        logger.info("\nTesting bank deposit (1.00% commission)...")
        publish_wallet_event(channel, 'wallet.debited', agent_id, amount, 'BANK_DEPOSIT')
        input("Press Enter to continue...")

    except KeyboardInterrupt:
        logger.info("Stopping test script...")
    finally:
        connection.close()

if __name__ == '__main__':
    main() 