from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Wallet
from .serializers import WalletSerializer, WalletBalanceSerializer
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for wallet operations.
    Provides read-only access to wallet information and balance.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter wallets by authenticated agent"""
        # Get the agent_id from the auth object
        agent_id = self.request.auth.agent_id if self.request.auth else None
        if not agent_id:
            return Wallet.objects.none()
        return Wallet.objects.filter(agent_id=agent_id)

    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get agent's wallet balance"""
        agent_id = request.auth.agent_id if request.auth else None
        if not agent_id:
            return Response({'detail': 'Agent ID not found in token'}, status=status.HTTP_404_NOT_FOUND)
        wallet = self.get_queryset().first()
        if not wallet:
            return Response({'detail': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'balance': str(wallet.balance)})

    @action(detail=False, methods=['post'])
    def check_balance(self, request):
        """
        Check if an agent has sufficient balance for a transaction
        """
        agent_id = request.auth.agent_id if request.auth else None
        amount = request.data.get('amount')
        
        if not agent_id:
            return Response(
                {'detail': 'Agent ID not found in token'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not amount:
            return Response(
                {'detail': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            wallet = Wallet.objects.get(agent_id=agent_id)
            amount = Decimal(str(amount))
            has_sufficient_balance = wallet.balance >= amount
            
            return Response({
                'has_sufficient_balance': has_sufficient_balance,
                'current_balance': str(wallet.balance),
                'required_amount': str(amount)
            })
            
        except Wallet.DoesNotExist:
            return Response(
                {'detail': 'Wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValueError, TypeError, InvalidOperation) as e:
            return Response(
                {'detail': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            ) 