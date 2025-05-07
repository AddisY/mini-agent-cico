from django.db import models
from enumchoicefield import ChoiceEnum, EnumChoiceField
from decimal import Decimal

class TransactionType(ChoiceEnum):
    WALLET_LOAD = "Wallet Load"
    BANK_DEPOSIT = "Bank Deposit"
    BANK_WITHDRAWAL = "Bank Withdrawal"

class WalletProvider(ChoiceEnum):
    TELEBIRR = "TeleBirr"
    MPESA = "M-Pesa"

class BankProvider(ChoiceEnum):
    CBE = "Commercial Bank of Ethiopia"
    DASHEN = "Dashen Bank"
    AWASH = "Awash Bank"
    ABYSSINIA = "Bank of Abyssinia"
    WEGAGEN = "Wegagen Bank"
    UNITED = "United Bank"
    NIB = "Nib International Bank"
    ZEMEN = "Zemen Bank"
    OROMIA = "Oromia International Bank"
    BERHAN = "Berhan International Bank"
    BUNNA = "Bunna Bank"
    ABAY = "Abay Bank"
    LION = "Lion International Bank"
    COOPERATIVE = "Cooperative Bank of Oromia"
    ADDIS = "Addis International Bank"
    ENAT = "Enat Bank"
    DEBUB = "Debub Global Bank"

class TransactionStatus(ChoiceEnum):
    INITIATED = "Initiated"
    SUCCESSFUL = "Successful"
    FAILED = "Failed"

class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True)
    transaction_type = EnumChoiceField(TransactionType, default=TransactionType.WALLET_LOAD)
    wallet_provider = EnumChoiceField(WalletProvider, null=True, blank=True)
    bank_provider = EnumChoiceField(BankProvider, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    agent_id = models.CharField(max_length=50)  # Changed from UUIDField to CharField to match wallet service
    customer_identifier = models.CharField(max_length=100)  # Phone number or account number
    status = EnumChoiceField(TransactionStatus, default=TransactionStatus.INITIATED)
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    commission_status = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type.value} - {self.status.value}"

    def get_provider_display(self):
        """Returns the display name of the provider based on transaction type"""
        if self.transaction_type == TransactionType.WALLET_LOAD:
            return self.wallet_provider.value if self.wallet_provider else None
        return self.bank_provider.value if self.bank_provider else None 