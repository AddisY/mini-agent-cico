import logging
from logging.handlers import RotatingFileHandler
from django.core.management.base import BaseCommand
from api.mq.consumer import EventConsumer

logger = logging.getLogger(__name__)

class DuplicateFilter(logging.Filter):
    def __init__(self, name=''):
        super().__init__(name)
        self.last_log = None

    def filter(self, record):
        # Allow if it's a different message
        current = (record.module, record.levelno, record.msg)
        if current != self.last_log:
            self.last_log = current
            return True
        return False

class Command(BaseCommand):
    help = 'Starts the RabbitMQ consumers for commission engine events'

    def handle(self, *args, **options):
        self.stdout.write('Starting commission engine consumers...')
        
        # Configure logging with rotation
        log_file = 'commission_engine.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in console
        
        # Add duplicate filter to both handlers
        duplicate_filter = DuplicateFilter()
        file_handler.addFilter(duplicate_filter)
        console_handler.addFilter(duplicate_filter)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.handlers = []  # Remove any existing handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Set appropriate log levels for specific loggers
        logging.getLogger('api.mq.consumer').setLevel(logging.INFO)
        logging.getLogger('api.mq.handlers').setLevel(logging.INFO)
        logging.getLogger('pika').setLevel(logging.WARNING)  # Reduce pika's verbosity

        consumer = EventConsumer()
        try:
            self.stdout.write(self.style.SUCCESS('Consumers started successfully'))
            consumer.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping consumers...'))
            consumer.stop()
            self.stdout.write(self.style.SUCCESS('Consumers stopped successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error starting consumers: {str(e)}'))
            logger.exception("Full traceback:")
            consumer.stop()
            raise 