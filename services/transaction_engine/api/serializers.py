from rest_framework import serializers
from .models import Transaction, TransactionType, WalletProvider, BankProvider

class TransactionSerializer(serializers.ModelSerializer):
    provider_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'transaction_type',
            'wallet_provider',
            'bank_provider',
            'provider_name',
            'amount',
            'agent_id',
            'customer_identifier',
            'status',
            'commission_amount',
            'commission_status',
            'error_message',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'status',
            'commission_amount',
            'commission_status',
            'error_message',
            'created_at',
            'updated_at'
        ]

    def get_provider_name(self, obj):
        return obj.get_provider_display()

    def validate(self, data):
        """
        Validate that the correct provider is set based on transaction type
        """
        transaction_type = data.get('transaction_type')
        wallet_provider = data.get('wallet_provider')
        bank_provider = data.get('bank_provider')

        if transaction_type == TransactionType.WALLET_LOAD:
            if not wallet_provider:
                raise serializers.ValidationError("Wallet provider is required for wallet load transactions")
            if bank_provider:
                raise serializers.ValidationError("Bank provider should not be set for wallet load transactions")
        else:  # Bank transactions
            if not bank_provider:
                raise serializers.ValidationError("Bank provider is required for bank transactions")
            if wallet_provider:
                raise serializers.ValidationError("Wallet provider should not be set for bank transactions")

        return data

class TransactionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for list views
    """
    provider_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'transaction_type',
            'provider_name',
            'amount',
            'customer_identifier',
            'status',
            'created_at'
        ]

    def get_provider_name(self, obj):
        return obj.get_provider_display() 