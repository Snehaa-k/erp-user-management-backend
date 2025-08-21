from rest_framework import serializers
from django.contrib.auth import authenticate
from companies.models import User, Company
from roles.models import Role, Permission, UserRole
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from audit.utils import log_action

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Audit failed attempt for non-existent user
            if request:
                from audit.models import AuditLog
                AuditLog.objects.create(
                    user=None,
                    action='LOGIN',
                    resource_type='User',
                    resource_id='unknown',
                    details=f'Failed login attempt for non-existent user: {email}',
                    ip_address=request.META.get('REMOTE_ADDR', 'unknown'),
                    user_agent='unknown'
                )
            raise serializers.ValidationError('Invalid credentials')

        # Check if account is locked
        if user.locked_until and user.locked_until > timezone.now():
            log_action(user, 'LOGIN', 'User', str(user.id), 'Failed login attempt - account locked', request)
            raise serializers.ValidationError('Account is temporarily locked')

        # Authenticate user
        authenticated_user = authenticate(username=user.username, password=password)
        if not authenticated_user:
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            if user.failed_login_attempts >= 5:  # ACCOUNT_LOCKOUT_ATTEMPTS
                user.locked_until = timezone.now() + timedelta(seconds=300)  # 5 minutes
            
            user.save()
            log_action(user, 'LOGIN', 'User', str(user.id), f'Failed login attempt #{user.failed_login_attempts}', request)
            raise serializers.ValidationError('Invalid credentials')

        # Reset failed attempts on successful login
        if authenticated_user.failed_login_attempts > 0:
            authenticated_user.failed_login_attempts = 0
            authenticated_user.locked_until = None
            authenticated_user.save()

        log_action(authenticated_user, 'LOGIN', 'User', str(authenticated_user.id), 'Successful login', request)
        attrs['user'] = authenticated_user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'company', 'permissions', 'roles', 'is_superuser']

    def get_permissions(self, obj):
        user_roles = UserRole.objects.filter(user=obj)
        permissions = set()
        for user_role in user_roles:
            role_permissions = user_role.role.permissions.all()
            permissions.update([perm.name for perm in role_permissions])
        return list(permissions)

    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(user=obj)
        return [{'id': ur.role.id, 'name': ur.role.name} for ur in user_roles]

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'company']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user