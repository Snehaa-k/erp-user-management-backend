from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'timestamp', 'company']
    list_filter = ['action', 'resource_type', 'timestamp', 'company']
    search_fields = ['user__username', 'resource_type', 'details']
    readonly_fields = ['user', 'company', 'action', 'resource_type', 'resource_id', 'details', 'ip_address', 'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False