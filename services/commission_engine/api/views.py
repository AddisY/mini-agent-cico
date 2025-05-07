from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from .models import CommissionRate, CommissionTransaction
from .serializers import CommissionRateSerializer, CommissionTransactionSerializer
from django.conf import settings

# Create your views here.

class CommissionRateViewSet(viewsets.ModelViewSet):
    queryset = CommissionRate.objects.all()
    serializer_class = CommissionRateSerializer
    lookup_field = 'agent_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        agent_id = self.request.query_params.get('agent_id')
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        # Cache the commission rate
        cache_key = f'commission_rate_{instance.agent_id}'
        cache.set(cache_key, instance, timeout=settings.CACHE_TTL)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Update cache
        cache_key = f'commission_rate_{instance.agent_id}'
        cache.set(cache_key, instance, timeout=settings.CACHE_TTL)

    @action(detail=True, methods=['post'])
    def toggle_eligibility(self, request, agent_id=None):
        commission_rate = self.get_object()
        commission_rate.is_eligible = not commission_rate.is_eligible
        commission_rate.save()
        
        # Update cache
        cache_key = f'commission_rate_{agent_id}'
        cache.set(cache_key, commission_rate, timeout=settings.CACHE_TTL)
        
        return Response(self.get_serializer(commission_rate).data)

class CommissionTransactionViewSet(viewsets.ModelViewSet):
    queryset = CommissionTransaction.objects.all()
    serializer_class = CommissionTransactionSerializer
    lookup_field = 'transaction_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        agent_id = self.request.query_params.get('agent_id')
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        return queryset

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, transaction_id=None):
        transaction = self.get_object()
        if transaction.status != CommissionTransaction.Status.PENDING:
            return Response(
                {'error': 'Only pending transactions can be marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = CommissionTransaction.Status.PAID
        transaction.save()
        return Response(self.get_serializer(transaction).data)
