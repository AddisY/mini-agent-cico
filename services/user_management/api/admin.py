from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Agent, AgentDocument

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'business_name', 'status', 'commission_rate')
    list_filter = ('status',)
    search_fields = ('agent_id', 'business_name', 'user__email')
    readonly_fields = ('agent_id', 'total_transactions')

@admin.register(AgentDocument)
class AgentDocumentAdmin(admin.ModelAdmin):
    list_display = ('agent', 'document_type', 'is_verified', 'uploaded_at')
    list_filter = ('document_type', 'is_verified')
    search_fields = ('agent__business_name', 'document_number')
    readonly_fields = ('uploaded_at', 'verified_at')
