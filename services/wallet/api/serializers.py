from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'agent_id', 'balance', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'agent_id', 'balance', 'created_at', 'updated_at']

class WalletBalanceSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True) 