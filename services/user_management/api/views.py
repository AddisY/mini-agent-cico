from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import logging
from .models import Agent, AgentDocument
from .serializers import (
    UserSerializer, UserCreateSerializer,
    AgentSerializer, AgentCreateSerializer,
    AgentDocumentSerializer, PasswordResetSerializer,
    EmailVerificationSerializer, CustomTokenObtainPairSerializer
)
from .permissions import IsAdmin, IsOwnerOrAdmin
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'phone_number']
    ordering_fields = ['created_at', 'email']
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'reset_password':
            return PasswordResetSerializer
        elif self.action == 'verify_email':
            return EmailVerificationSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"New user created: {user.email}")
        self.send_verification_email(user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def verify(self, request, pk=None):
        user = self.get_object()
        user.is_verified = True
        user.save()
        logger.info(f"User verified by admin: {user.email}")
        return Response({'status': 'user verified'})

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
            
            # Send password reset email
            context = {'user': user, 'reset_link': reset_link}
            email_html = render_to_string('password_reset_email.html', context)
            send_mail(
                'Password Reset Request',
                'Please click the link to reset your password',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=email_html
            )
            logger.info(f"Password reset email sent to: {email}")
            
        except User.DoesNotExist:
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            pass  # Don't reveal if email exists
        
        return Response({'status': 'password reset email sent if email exists'})

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            if not user.is_verified:
                self.send_verification_email(user)
                logger.info(f"Verification email resent to: {user.email}")
            
        except User.DoesNotExist:
            logger.warning(f"Email verification attempted for non-existent email")
            pass
        
        return Response({'status': 'verification email sent if email exists'})

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
        
        context = {'user': user, 'verification_link': verification_link}
        email_html = render_to_string('email_verification.html', context)
        
        send_mail(
            'Verify Your Email',
            'Please verify your email address',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=email_html
        )

class AgentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [UserRateThrottle]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['business_name', 'agent_id', 'user__email']
    ordering_fields = ['created_at', 'business_name']
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Agent.objects.all()
        return Agent.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AgentCreateSerializer
        return AgentSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            agent = Agent.objects.get(user=request.user)
            serializer = self.get_serializer(agent)
            return Response(serializer.data)
        except Agent.DoesNotExist:
            return Response(
                {"detail": "Agent profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def perform_create(self, serializer):
        agent = serializer.save()
        logger.info(f"New agent created: {agent.business_name} ({agent.agent_id})")

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def activate(self, request, pk=None):
        agent = self.get_object()
        agent.status = 'ACTIVE'
        agent.save()
        logger.info(f"Agent activated: {agent.agent_id}")
        return Response({'status': 'agent activated'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def suspend(self, request, pk=None):
        agent = self.get_object()
        agent.status = 'SUSPENDED'
        agent.save()
        logger.info(f"Agent suspended: {agent.agent_id}")
        return Response({'status': 'agent suspended'})

class AgentDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = AgentDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [UserRateThrottle]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['document_type', 'document_number', 'agent__business_name']
    ordering_fields = ['uploaded_at', 'document_type']
    
    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return AgentDocument.objects.all()
        return AgentDocument.objects.filter(agent__user=self.request.user)

    def perform_create(self, serializer):
        document = serializer.save()
        logger.info(f"New document uploaded: {document.document_type} for agent {document.agent.agent_id}")

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def verify_document(self, request, pk=None):
        document = self.get_object()
        document.is_verified = True
        document.save()
        logger.info(f"Document verified: {document.document_type} for agent {document.agent.agent_id}")
        return Response({'status': 'document verified'})

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_field(request):
    field = request.data.get('field')
    value = request.data.get('value')
    
    if not field or not value:
        return Response(
            {'error': 'Both field and value are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if field not in ['email', 'username']:
        return Response(
            {'error': 'Invalid field'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if email/username exists
    exists = User.objects.filter(**{field: value}).exists()
    
    if exists:
        error_messages = {
            'email': 'This email is already registered',
            'username': 'This username is already taken'
        }
        return Response({'error': error_messages[field]}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'valid': True})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        logger.info(f"Login attempt for email: {email}")

        if not email or not password:
            logger.warning("Login attempt without email or password")
            return Response(
                {'detail': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request=request, username=email, password=password)
        logger.info(f"Authentication result for {email}: {'Success' if user else 'Failed'}")

        if not user:
            return Response(
                {'detail': 'Incorrect email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }
        logger.info(f"Login successful for user: {email}")
        return Response(response_data)
