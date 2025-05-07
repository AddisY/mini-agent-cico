import threading
import logging
from django.core.management.base import BaseCommand
from api.mq.client import RabbitMQClient
from api.mq.handlers import TransactionEventHandler as EventHandler

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start RabbitMQ consumers for transaction service'

    def handle(self, *args, **options):
        def start_consumer(queue_name, callback):
            with RabbitMQClient() as client:
                self.stdout.write(
                    self.style.SUCCESS(f'Starting consumer for queue: {queue_name}')
                )
                client.consume(queue_name, callback)

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

        threads = []
        for consumer in consumers:
            thread = threading.Thread(
                target=start_consumer,
                args=(consumer['queue'], consumer['callback']),
                daemon=True
            )
            thread.start()
            threads.append(thread)

        # Keep the main thread alive
        for thread in threads:
            thread.join() 