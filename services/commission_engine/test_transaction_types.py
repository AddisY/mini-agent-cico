import json
import logging
import uuid
from decimal import Decimal
import pika
from django.test import TestCase
from api.models import CommissionRate, CommissionTransaction, TransactionType
from api.mq.handlers import EventHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockChannel:
    def basic_ack(self, delivery_tag):
        pass

    def basic_nack(self, delivery_tag, requeue=False):
        pass

class MockMethod:
    def __init__(self, routing_key):
        self.routing_key = routing_key
        self.delivery_tag = 1

class TestTransactionTypeHandling(TestCase):
    def setUp(self):
        self.agent_id = str(uuid.uuid4())
        self.handler = EventHandler()
        self.mock_channel = MockChannel()
        
        # Create commission rates for the test agent
        CommissionRate.objects.create(
            agent_id=self.agent_id,
            wallet_load_rate=Decimal('1.50'),
            bank_deposit_rate=Decimal('1.00'),
            bank_withdrawal_rate=Decimal('1.25')
        )

    def test_bank_withdrawal_transaction(self):
        """Test handling of a bank withdrawal transaction"""
        transaction_id = str(uuid.uuid4())
        
        # Simulate a wallet.credited event for bank withdrawal
        event_data = {
            'transaction_id': transaction_id,
            'agent_id': self.agent_id,
            'amount': '1000.00',
            'transaction_type': 'BANK_WITHDRAWAL'  # This should be preserved
        }
        
        # Process the event
        self.handler.handle_wallet_event(
            self.mock_channel,
            MockMethod('wallet.credited'),
            None,
            json.dumps(event_data).encode()
        )
        
        # Verify the commission transaction was created with correct type
        commission_tx = CommissionTransaction.objects.get(transaction_id=transaction_id)
        self.assertEqual(commission_tx.transaction_type, TransactionType.BANK_WITHDRAWAL)
        self.assertEqual(commission_tx.agent_id, self.agent_id)
        
        # Verify commission amount calculation (1.25% for bank withdrawal)
        expected_commission = Decimal('1000.00') * Decimal('1.25') / Decimal('100')
        self.assertEqual(commission_tx.commission_amount, expected_commission)

    def test_wallet_load_transaction(self):
        """Test handling of a wallet load transaction"""
        transaction_id = str(uuid.uuid4())
        
        # Simulate a wallet.debited event for wallet load
        event_data = {
            'transaction_id': transaction_id,
            'agent_id': self.agent_id,
            'amount': '500.00',
            'transaction_type': 'WALLET_LOAD'  # This should be preserved
        }
        
        # Process the event
        self.handler.handle_wallet_event(
            self.mock_channel,
            MockMethod('wallet.debited'),
            None,
            json.dumps(event_data).encode()
        )
        
        # Verify the commission transaction was created with correct type
        commission_tx = CommissionTransaction.objects.get(transaction_id=transaction_id)
        self.assertEqual(commission_tx.transaction_type, TransactionType.WALLET_LOAD)
        self.assertEqual(commission_tx.agent_id, self.agent_id)
        
        # Verify commission amount calculation (1.50% for wallet load)
        expected_commission = Decimal('500.00') * Decimal('1.50') / Decimal('100')
        self.assertEqual(commission_tx.commission_amount, expected_commission)

    def test_missing_transaction_type(self):
        """Test that events without transaction_type are rejected"""
        transaction_id = str(uuid.uuid4())
        
        # Simulate event without transaction_type
        event_data = {
            'transaction_id': transaction_id,
            'agent_id': self.agent_id,
            'amount': '1000.00'
        }
        
        # Process the event
        self.handler.handle_wallet_event(
            self.mock_channel,
            MockMethod('wallet.credited'),
            None,
            json.dumps(event_data).encode()
        )
        
        # Verify no commission transaction was created
        self.assertFalse(
            CommissionTransaction.objects.filter(transaction_id=transaction_id).exists()
        )

    def test_invalid_transaction_type(self):
        """Test that events with invalid transaction_type are rejected"""
        transaction_id = str(uuid.uuid4())
        
        # Simulate event with invalid transaction_type
        event_data = {
            'transaction_id': transaction_id,
            'agent_id': self.agent_id,
            'amount': '1000.00',
            'transaction_type': 'INVALID_TYPE'
        }
        
        # Process the event
        self.handler.handle_wallet_event(
            self.mock_channel,
            MockMethod('wallet.credited'),
            None,
            json.dumps(event_data).encode()
        )
        
        # Verify no commission transaction was created
        self.assertFalse(
            CommissionTransaction.objects.filter(transaction_id=transaction_id).exists()
        ) 