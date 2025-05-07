import threading
import logging
import time
import signal
import sys
from django.core.management.base import BaseCommand
from api.mq.client import RabbitMQClient
from api.mq.handlers import EventHandler
from api.mq.consumer import EventConsumer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts RabbitMQ consumers'
    
    def __init__(self):
        super().__init__()
        self.consumers = []
        self.stop_event = threading.Event()
    
    def handle(self, *args, **options):
        # Define consumer configurations
        consumer_configs = [
            {
                'queue': 'wallet_agent_events',
                'exchange': 'user_events',
                'routing_key': 'agent.created'
            },
            {
                'queue': 'wallet_transaction_events',
                'exchange': 'transaction_events',
                'routing_key': 'transaction.initiated'
            },
            {
                'queue': 'commission_events',
                'exchange': 'commission_events',
                'routing_key': 'commission.recorded'
            }
        ]
        
        # Start consumers in separate threads
        for config in consumer_configs:
            consumer = EventConsumer()
            thread = threading.Thread(
                target=self._run_consumer,
                args=(consumer, config['queue']),
                name=f"Consumer-{len(self.consumers)+1}-{config['queue']}"
            )
            thread.daemon = True
            self.consumers.append((thread, consumer))
            thread.start()
            self.stdout.write(f"Starting consumer for queue: {config['queue']}")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        # Keep the main thread alive
        try:
            while not self.stop_event.is_set():
                self.stop_event.wait(1)
        except KeyboardInterrupt:
            self._shutdown()
    
    def _run_consumer(self, consumer, queue_name):
        try:
            consumer.start()
        except Exception as e:
            logger.error(f"Consumer for {queue_name} failed: {str(e)}")
            self.stop_event.set()
    
    def _handle_shutdown(self, signum, frame):
        self._shutdown()
    
    def _shutdown(self):
        self.stdout.write("\nShutting down consumers...")
        self.stop_event.set()
        
        for thread, consumer in self.consumers:
            try:
                consumer.stop()
                if thread.is_alive():
                    self.stdout.write(f"Force stopping thread {thread.name}...")
                    thread.join(timeout=1)
            except Exception as e:
                logger.error(f"Error stopping consumer thread {thread.name}: {str(e)}")
        
        self.stdout.write("Consumers shut down successfully")
        sys.exit(0) 