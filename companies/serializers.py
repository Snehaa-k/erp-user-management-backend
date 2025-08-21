from rest_framework import serializers
from .models import Company, User, UserPassword
from roles.models import UserRole

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']

class UserListSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    current_password = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'roles', 'current_password', 'company']
    
    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(user=obj)
        return [{'id': ur.role.id, 'name': ur.role.name} for ur in user_roles]
    
    def get_current_password(self, obj):
        try:
            return obj.stored_password.password_text
        except UserPassword.DoesNotExist:
            return None
    
    def get_company(self, obj):
        if obj.company:
            return {'id': obj.company.id, 'name': obj.company.name}
        return None

class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_active']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        request_user = self.context['request'].user
        
        # Superusers can create users and assign them to any company
        if request_user.is_superuser:
            # Company is optional for superusers - they can create users without company initially
            pass
        else:
            # Regular users can only create users for their company
            if hasattr(request_user, 'company') and request_user.company:
                validated_data['company'] = request_user.company
            else:
                raise serializers.ValidationError('User must belong to a company')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Store readable password
        UserPassword.objects.create(user=user, password_text=password)
        
        # Store password to return to admin
        user._admin_password = password
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Include password in response for admin
        if hasattr(instance, '_admin_password'):
            data['password'] = instance._admin_password
        return data
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
            # Update stored password
            UserPassword.objects.update_or_create(
                user=instance,
                defaults={'password_text': password}
            )
        instance.save()
        return instance