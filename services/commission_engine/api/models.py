from django.db import models
from enumchoicefield import ChoiceEnum, EnumChoiceField
from decimal import Decimal

# Create your models here.

class TransactionType(ChoiceEnum):
    WALLET_LOAD = "WALLET_LOAD"
    BANK_DEPOSIT = "BANK_DEPOSIT"
    BANK_WITHDRAWAL = "BANK_WITHDRAWAL"

class TransactionStatus(ChoiceEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"

class CommissionRate(models.Model):
    agent_id = models.CharField(max_length=100, unique=True)
    wallet_load_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.50'))
    bank_deposit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    bank_withdrawal_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.25'))
    is_eligible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_rate_for_transaction_type(self, transaction_type: TransactionType) -> Decimal:
        """Get commission rate for a specific transaction type"""
        rate_map = {
            TransactionType.WALLET_LOAD: self.wallet_load_rate,
            TransactionType.BANK_DEPOSIT: self.bank_deposit_rate,
            TransactionType.BANK_WITHDRAWAL: self.bank_withdrawal_rate,
        }
        return rate_map.get(transaction_type, Decimal('0.00'))

    class Meta:
        db_table = 'commission_rates'
        ordering = ['-created_at']

class CommissionTransaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    agent_id = models.CharField(max_length=100)
    transaction_type = EnumChoiceField(TransactionType, max_length=20)
    transaction_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = EnumChoiceField(TransactionStatus, max_length=10, default=TransactionStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'commission_transactions'
        ordering = ['-created_at']
