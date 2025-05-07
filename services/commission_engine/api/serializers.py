from rest_framework import serializers
from .models import CommissionRate, CommissionTransaction

class CommissionRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRate
        fields = [
            'agent_id',
            'wallet_load_rate',
            'bank_deposit_rate',
            'bank_withdrawal_rate',
            'is_eligible',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CommissionTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionTransaction
        fields = [
            'transaction_id',
            'agent_id',
            'transaction_type',
            'transaction_amount',
            'commission_rate',
            'commission_amount',
            'status',
            'created_at',
            'paid_at'
        ]
        read_only_fields = ['created_at', 'paid_at'] 