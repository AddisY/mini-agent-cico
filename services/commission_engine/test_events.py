import pika
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    """Handle received messages"""
    try:
        data = json.loads(body)
        logger.info(f"Received event: {method.routing_key}")
        logger.info(f"Event data: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        logger.error(f"Failed to decode message: {body}")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

def main():
    # Connect to RabbitMQ
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
    exchange_name = 'commission_events'
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type='topic',
        durable=True
    )
    
    # Create a temporary queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    # Bind to commission events
    routing_keys = ['commission.recorded', 'commission.skipped']
    for key in routing_keys:
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=key
        )
    
    logger.info(f"Listening for commission events: {', '.join(routing_keys)}")
    
    # Start consuming
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping event listener...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == '__main__':
    main() 