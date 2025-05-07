from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import validate_email
from .models import Agent, AgentDocument
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from .mq.client import RabbitMQClient

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    agent_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'role', 'is_verified', 'created_at', 'updated_at', 'agent_id')
        read_only_fields = ('id', 'created_at', 'updated_at', 'agent_id')

    def get_agent_id(self, obj):
        """Get agent_id if user is an agent"""
        if obj.role == 'AGENT':
            try:
                agent = Agent.objects.get(user=obj)
                return agent.agent_id
            except Agent.DoesNotExist:
                return None
        return None

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(validators=[validate_email])
    phone_number = serializers.CharField(max_length=15)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'phone_number', 'role', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken")
        return value

    def validate_phone_number(self, value):
        # Remove the + symbol if it exists at the start
        number_to_check = value[1:] if value.startswith('+') else value
        
        # Check if the remaining characters are digits
        if not number_to_check.isdigit():
            raise serializers.ValidationError("Phone number can only contain digits and optionally start with +")
        
        # Check the minimum length (9 digits)
        if len(number_to_check) < 9:
            raise serializers.ValidationError("Phone number must contain at least 9 digits")
        
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[validate_email])

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[validate_email])

class AgentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentDocument
        fields = '__all__'
        read_only_fields = ('is_verified', 'verified_at')

    def validate_document_file(self, value):
        # Validate file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 5MB")
        
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("File type must be PDF, JPEG, or PNG")
            
        return value

class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    documents = AgentDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Agent
        fields = ('id', 'user', 'agent_id', 'business_name', 'business_address', 
                 'status', 'commission_rate', 'total_transactions',
                 'created_at', 'updated_at', 'documents')
        read_only_fields = ('id', 'total_transactions', 'created_at', 'updated_at')

class AgentCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    
    class Meta:
        model = Agent
        fields = ('user', 'business_name', 'business_address', 'commission_rate')

    def validate_commission_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Commission rate must be between 0 and 100")
        return value

    def validate_business_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Business name must be at least 3 characters long")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'AGENT'
        user_serializer = UserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        # Generate a unique agent_id
        import uuid
        agent_id = f"AG{str(uuid.uuid4().hex[:8]).upper()}"
        
        agent = Agent.objects.create(
            user=user,
            agent_id=agent_id,
            **validated_data
        )

        # Publish agent.created event
        try:
            with RabbitMQClient() as client:
                client.publish_event(
                    routing_key='agent.created',
                    data={
                        'agent_id': agent_id,
                        'business_name': agent.business_name,
                        'status': agent.status
                    }
                )
        except Exception as e:
            # Log the error but don't prevent agent creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to publish agent.created event: {str(e)}")

        return agent

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        authenticate_kwargs = {
            'email': attrs['email'],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        user = authenticate(**authenticate_kwargs)

        if not user:
            raise serializers.ValidationError(
                _('Incorrect email or password'),
                code='authorization'
            )

        refresh = self.get_token(user)

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        } 