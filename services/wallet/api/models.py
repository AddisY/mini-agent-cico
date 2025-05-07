from django.db import models
import uuid
from decimal import Decimal

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
        if is_credit:
            self.balance += amount
        else:
            if self.balance < amount:
                raise ValueError('Insufficient balance')
            self.balance -= amount
        self.save() 