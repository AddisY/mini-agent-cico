import threading
from django.core.management.base import BaseCommand
from api.mq.client import RabbitMQClient
from api.mq.handlers import EventHandler

class Command(BaseCommand):
    help = 'Start RabbitMQ consumers for wallet service'

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
                'queue': 'wallet_agent_events',
                'callback': EventHandler.handle_agent_created
            },
            {
                'queue': 'wallet_transaction_events',
                'callback': EventHandler.handle_transaction_event
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