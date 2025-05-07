from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('AGENT', 'Agent'),
        ('MERCHANT', 'Merchant'),
    )

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='AGENT')
    phone_number = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

class Agent(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    agent_id = models.CharField(max_length=20, unique=True)
    business_name = models.CharField(max_length=100)
    business_address = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='INACTIVE')
    commission_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0)  # Percentage
    total_transactions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} ({self.agent_id})"

class AgentDocument(models.Model):
    DOCUMENT_TYPES = (
        ('ID', 'National ID'),
        ('PASSPORT', 'Passport'),
        ('BUSINESS_LICENSE', 'Business License'),
        ('TAX_CERT', 'Tax Certificate'),
    )

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=50)
    document_file = models.FileField(upload_to='agent_documents/')
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['agent', 'document_type']

    def __str__(self):
        return f"{self.agent.business_name} - {self.get_document_type_display()}"
