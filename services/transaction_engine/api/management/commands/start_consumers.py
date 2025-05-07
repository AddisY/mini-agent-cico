import threading
import logging
import time
import signal
import sys
from django.core.management.base import BaseCommand
from api.mq.client import RabbitMQClient
from api.mq.handlers import TransactionEventHandler as EventHandler

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start RabbitMQ consumers for transaction service'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shutdown_event = threading.Event()
        self.threads = []
        self._shutdown_timeout = 1  # seconds

    def handle(self, *args, **options):
        def signal_handler(signum, frame):
            """Handle shutdown signals"""
            self.stdout.write(self.style.WARNING('\nShutting down consumers...'))
            self._shutdown_event.set()
            
            # Wait for threads with timeout
            shutdown_start = time.time()
            for thread in self.threads:
                remaining_timeout = max(0, self._shutdown_timeout - (time.time() - shutdown_start))
                thread.join(timeout=remaining_timeout)
                if thread.is_alive():
                    self.stdout.write(self.style.WARNING(f'Force stopping thread {thread.name}...'))
            
            self.stdout.write(self.style.SUCCESS('Consumers shut down successfully'))
            sys.exit(0)

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        def start_consumer(queue_name, callback):
            client = None
            while not self._shutdown_event.is_set():
                try:
                    with RabbitMQClient() as client:
                        self.stdout.write(
                            self.style.SUCCESS(f'Starting consumer for queue: {queue_name}')
                        )
                        client.consume(queue_name, callback)
                except Exception as e:
                    if not self._shutdown_event.is_set():
                        logger.error(f"Consumer for {queue_name} encountered an error: {str(e)}")
                        logger.info(f"Attempting to restart consumer for {queue_name} in 5 seconds...")
                        # Use the shutdown event as a timer to allow interruption
                        self._shutdown_event.wait(timeout=5)
                    else:
                        break

        # Start consumers in separate threads
        consumers = [
            {
                'queue': 'transaction_status_events',
                'callback': EventHandler.handle_transaction_failed
            },
            {
                'queue': 'transaction_completion_events',
                'callback': EventHandler.handle_transaction_completed
            }
        ]

        self.threads = []
        for i, consumer in enumerate(consumers):
            thread = threading.Thread(
                target=start_consumer,
                args=(consumer['queue'], consumer['callback']),
                name=f"Consumer-{i+1}-{consumer['queue']}",
                daemon=True
            )
            thread.start()
            self.threads.append(thread)

        # Keep the main thread alive and responsive to signals
        try:
            while not self._shutdown_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            # This block might not be reached due to the signal handler,
            # but it's here as a fallback
            self.stdout.write(self.style.WARNING('\nShutting down consumers...'))
            self._shutdown_event.set()
            
            # Wait for threads with timeout
            shutdown_start = time.time()
            for thread in self.threads:
                remaining_timeout = max(0, self._shutdown_timeout - (time.time() - shutdown_start))
                thread.join(timeout=remaining_timeout)
                if thread.is_alive():
                    self.stdout.write(self.style.WARNING(f'Force stopping thread {thread.name}...'))
            
            self.stdout.write(self.style.SUCCESS('Consumers shut down successfully'))
            sys.exit(0) 