import pika
import json
import logging
import time
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
        exchange='transaction_events',
        exchange_type='topic',
        durable=True
    )
    
    return connection, channel

def publish_transaction(channel, transaction_id, agent_id, amount, transaction_type, status):
    """Publish a transaction event"""
    message = {
        'transaction_id': transaction_id,
        'agent_id': agent_id,
        'amount': str(amount),
        'transaction_type': transaction_type,
        'status': status
    }
    
    channel.basic_publish(
        exchange='transaction_events',
        routing_key='transaction.status',
        body=json.dumps(message)
    )
    logger.info(f"Published transaction event: {message}")

def test_transactions():
    """Run test scenarios"""
    try:
        connection, channel = connect_rabbitmq()
        
        # Test scenario 1: Wallet Load (should debit agent's wallet)
        publish_transaction(
            channel=channel,
            transaction_id='test_load_1',
            agent_id='AG3AF8BC02',  # Use an existing agent ID
            amount=Decimal('100.00'),
            transaction_type='WALLET_LOAD',
            status='SUCCESSFUL'
        )
        time.sleep(2)  # Wait for processing
        
        # Test scenario 2: Bank Deposit (should debit agent's wallet)
        publish_transaction(
            channel=channel,
            transaction_id='test_deposit_1',
            agent_id='AG3AF8BC02',
            amount=Decimal('50.00'),
            transaction_type='BANK_DEPOSIT',
            status='SUCCESSFUL'
        )
        time.sleep(2)
        
        # Test scenario 3: Bank Withdrawal (should credit agent's wallet)
        publish_transaction(
            channel=channel,
            transaction_id='test_withdraw_1',
            agent_id='AG3AF8BC02',
            amount=Decimal('25.00'),
            transaction_type='BANK_WITHDRAWAL',
            status='SUCCESSFUL'
        )
        time.sleep(2)
        
        # Close connection
        connection.close()
        logger.info("Test scenarios completed")
        
    except Exception as e:
        logger.error(f"Error running test scenarios: {str(e)}")
        raise

if __name__ == '__main__':
    test_transactions() 