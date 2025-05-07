from django.db import models
import uuid
from decimal import Decimal
import logging

class Wallet(models.Model):
    """
    Represents an agent's wallet for managing float balance.
    Each agent has exactly one wallet that is created automatically.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=50, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'wallets'
        ordering = ['-created_at']

    def __str__(self):
        return f"Wallet {self.id} - Agent {self.agent_id}"

    def update_balance(self, amount: Decimal, is_credit: bool) -> None:
        """
        Update wallet balance
        :param amount: Amount to add or subtract
        :param is_credit: True for credit (add), False for debit (subtract)
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Updating wallet {self.id} balance: Current={self.balance}, Amount={amount}, Operation={'credit' if is_credit else 'debit'}")
        
        if is_credit:
            self.balance += amount
            logger.info(f"Credited amount {amount}. New balance: {self.balance}")
        else:
            if self.balance < amount:
                logger.error(f"Insufficient balance: Required={amount}, Available={self.balance}")
                raise ValueError('Insufficient balance')
            self.balance -= amount
            logger.info(f"Debited amount {amount}. New balance: {self.balance}")
        
        self.save()
        logger.info(f"Wallet balance updated and saved successfully. Final balance: {self.balance}") 