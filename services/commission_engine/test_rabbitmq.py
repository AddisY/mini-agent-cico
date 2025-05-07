import pika
import logging
import traceback
import json
import time

# Set up logging to write to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rabbitmq_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Attempting to connect to RabbitMQ...")
    
    # Create connection parameters
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=credentials,
        connection_attempts=3,
        retry_delay=2
    )
    
    logger.info("Connection parameters created, attempting to establish connection...")
    
    # Try to establish connection
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    logger.info("Successfully connected to RabbitMQ!")
    
    # Declare the exchange we're using
    channel.exchange_declare(
        exchange='kifiya',
        exchange_type='topic',
        durable=True
    )
    logger.info("Successfully declared exchange 'kifiya'")
    
    # Declare the queue
    channel.queue_declare(queue='agent.created', durable=True)
    channel.queue_bind(
        exchange='kifiya',
        queue='agent.created',
        routing_key='agent.created'
    )
    logger.info("Successfully declared and bound queue: agent.created")
    
    # Test message for agent creation
    test_message = {
        "agent_id": "test_agent_123",
        "name": "Test Agent",
        "email": "test@example.com"
    }
    
    # Publish test message
    channel.basic_publish(
        exchange='kifiya',
        routing_key='agent.created',
        body=json.dumps(test_message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            content_type='application/json'
        )
    )
    logger.info(f"Published test message: {test_message}")
    
    # Verify the message was published
    method_frame, header_frame, body = channel.basic_get('agent.created')
    if method_frame:
        logger.info("Successfully retrieved the published message!")
        logger.info(f"Message body: {body.decode()}")
        channel.basic_nack(method_frame.delivery_tag)  # Put the message back in the queue
    else:
        logger.error("Failed to retrieve the published message!")
    
    # Wait a moment to ensure message is processed
    time.sleep(2)
    
    # Close the connection
    connection.close()
    logger.info("Connection closed successfully")
    
except Exception as e:
    logger.error("Failed to connect to RabbitMQ")
    logger.error(f"Error type: {type(e).__name__}")
    logger.error(f"Error message: {str(e)}")
    logger.error("Traceback:")
    logger.error(traceback.format_exc())
    with open('rabbitmq_error.txt', 'w') as f:
        f.write(f"Error type: {type(e).__name__}\n")
        f.write(f"Error message: {str(e)}\n")
        f.write("Traceback:\n")
        f.write(traceback.format_exc())
    raise 