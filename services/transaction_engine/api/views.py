import uuid
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db.models import Q, Sum, Count
from .models import Transaction, TransactionType, TransactionStatus
from .serializers import TransactionSerializer, TransactionListSerializer
from .mq.client import RabbitMQClient
from .services.wallet import WalletServiceClient
from decimal import Decimal

logger = logging.getLogger(__name__)

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer

    def get_queryset(self):
        """
        Filter transactions by agent_id from the authenticated user
        """
        queryset = Transaction.objects.filter(agent_id=self.request.user.id)
        
        # Apply filters if provided
        status = self.request.query_params.get('status', None)
        transaction_type = self.request.query_params.get('type', None)
        provider = self.request.query_params.get('provider', None)

        if status:
            queryset = queryset.filter(status=status)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if provider:
            queryset = queryset.filter(
                Q(wallet_provider=provider) | Q(bank_provider=provider)
            )

        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Create a new transaction and publish initiated event
        """
        try:
            # Generate transaction_id
            transaction_id = str(uuid.uuid4())
            logger.info(f"Generated transaction_id: {transaction_id}")

            # Create mutable copy of request data
            data = request.data.copy()
            
            # Add transaction_id and agent_id
            data['transaction_id'] = transaction_id
            data['agent_id'] = request.user.agent_id  # Use the agent_id from the agent profile
            
            logger.info(f"Request data after adding IDs: {data}")

            serializer = self.get_serializer(data=data)
            
            if not serializer.is_valid():
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Check balance for non-credit transactions
            transaction_type = data.get('transaction_type')
            if transaction_type not in [TransactionType.WALLET_LOAD.value, TransactionType.BANK_DEPOSIT.value]:
                wallet_client = WalletServiceClient()
                has_balance, error_message = wallet_client.check_balance(
                    agent_id=request.user.agent_id,
                    amount=serializer.validated_data['amount'],
                    auth_token=request.headers.get('Authorization')
                )
                
                if not has_balance:
                    # Create failed transaction record
                    transaction = serializer.save(
                        status=TransactionStatus.FAILED,
                        error_message=error_message
                    )
                    return Response(
                        {
                            "error": "Insufficient balance",
                            "detail": error_message,
                            "transaction_id": transaction.transaction_id
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            try:
                # Create transaction
                transaction = serializer.save()
                logger.info(f"Transaction created successfully: {transaction.transaction_id}")
                
                # Publish event
                try:
                    with RabbitMQClient() as mq_client:
                        mq_client.publish(
                            routing_key='transaction.initiated',
                            message={
                                'transaction_id': str(transaction.transaction_id),
                                'transaction_type': transaction.transaction_type.name,
                                'amount': str(transaction.amount),
                                'agent_id': str(transaction.agent_id),
                                'customer_identifier': transaction.customer_identifier,
                                'provider': transaction.get_provider_display(),
                                'status': TransactionStatus.INITIATED.name
                            }
                        )
                        logger.info("Transaction initiated event published successfully")
                except Exception as e:
                    logger.error(f"Failed to publish transaction event: {str(e)}")
                    # Don't fail the request if event publishing fails
                    # We might want to implement a retry mechanism here

                # Cache transaction
                try:
                    cache_key = f"transaction_{transaction.transaction_id}"
                    cache.set(cache_key, transaction, timeout=3600)  # 1 hour
                    logger.info(f"Transaction cached with key: {cache_key}")
                except Exception as e:
                    logger.error(f"Failed to cache transaction: {str(e)}")
                    # Don't fail the request if caching fails

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                logger.error(f"Failed to save transaction: {str(e)}")
                return Response(
                    {
                        "error": "Failed to save transaction",
                        "detail": str(e)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Unexpected error in create transaction: {str(e)}")
            return Response(
                {
                    "error": "An unexpected error occurred",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Get transaction details with cache support
        """
        transaction_id = kwargs.get('pk')
        cache_key = f"transaction_{transaction_id}"

        # Try to get from cache first
        transaction = cache.get(cache_key)
        if transaction:
            serializer = self.get_serializer(transaction)
            return Response(serializer.data)

        # If not in cache, get from database
        try:
            transaction = self.get_queryset().get(transaction_id=transaction_id)
            serializer = self.get_serializer(transaction)
            
            # Cache for future requests
            cache.set(cache_key, transaction, timeout=3600)  # 1 hour
            
            return Response(serializer.data)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get transaction statistics for the authenticated agent
        """
        try:
            queryset = self.get_queryset()
            
            # Calculate statistics
            stats = {
                'total_transactions': queryset.count(),
                'total_amount': str(queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')),
                'successful_transactions': queryset.filter(status=TransactionStatus.SUCCESSFUL).count(),
                'successful_amount': str(
                    queryset.filter(status=TransactionStatus.SUCCESSFUL)
                    .aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                ),
                'failed_transactions': queryset.filter(status=TransactionStatus.FAILED).count(),
                'pending_transactions': queryset.filter(status=TransactionStatus.INITIATED).count(),
                'total_commission_earned': str(
                    queryset.filter(
                        status=TransactionStatus.SUCCESSFUL,
                        commission_status=True
                    ).aggregate(total=Sum('commission_amount'))['total'] or Decimal('0.00')
                )
            }
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting transaction stats: {str(e)}")
            return Response(
                {"error": "Failed to get transaction statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def providers(self, request):
        """
        Get list of available providers based on transaction type
        """
        transaction_type = request.query_params.get('type')
        
        if not transaction_type:
            return Response(
                {"error": "Transaction type is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if transaction_type == TransactionType.WALLET_LOAD.value:
                from .models import WalletProvider
                providers = [{"id": p.value, "name": p.value} for p in WalletProvider]
            else:
                from .models import BankProvider
                providers = [{"id": p.value, "name": p.value} for p in BankProvider]

            return Response(providers)
        except ValueError:
            return Response(
                {"error": "Invalid transaction type"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def transaction_types(self, request):
        """
        Get list of available transaction types
        """
        types = [{"id": t.value, "name": t.value} for t in TransactionType]
        return Response(types) 