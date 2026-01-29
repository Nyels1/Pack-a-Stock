from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'user', 'account', 'table_name', 'record_id', 'created_at']
    list_filter = ['action', 'account', 'created_at']
    search_fields = ['user__full_name', 'user__email', 'description', 'table_name']
    readonly_fields = ['account', 'user', 'action', 'table_name', 'record_id', 
                      'changes', 'ip_address', 'user_agent', 'description', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
