from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_type', 'get_provider', 'amount', 
                   'agent_id', 'customer_identifier', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'wallet_provider', 'bank_provider', 
                  'commission_status', 'created_at')
    search_fields = ('transaction_id', 'agent_id', 'customer_identifier')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_provider(self, obj):
        return obj.get_provider_display()
    get_provider.short_description = 'Provider' 