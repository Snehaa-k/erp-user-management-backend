from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user_name', 'user_email', 'action', 'resource_type', 'resource_id', 'details', 'timestamp']
    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'System'
    
    def get_user_email(self, obj):
        return obj.user.email if obj.user else 'N/A'