from rest_framework import serializers
from .models import Role, Permission, UserRole

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'description']

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'created_at', 'updated_at']
    
    def get_permissions(self, obj):
        return [perm.name for perm in obj.permissions.all()]

class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name', 'description']
    
    def create(self, validated_data):
        request_user = self.context['request'].user
        
        # Only superusers can create roles (system-wide roles)
        if not request_user.is_superuser:
            raise serializers.ValidationError('Only superusers can create roles')
        
        return super().create(validated_data)

class AssignPermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.CharField())