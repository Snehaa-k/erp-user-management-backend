from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from .serializers import LoginSerializer, UserSerializer, UserCreateSerializer
from companies.models import User
from roles.models import UserRole
from audit.models import AuditLog
from audit.utils import log_action

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        
        # Get effective permissions (computed union of all assigned roles)
        if user.is_superuser:
            # Superusers get all permissions
            from roles.models import Permission
            all_permissions = Permission.objects.all()
            permissions_list = [perm.name for perm in all_permissions]
        else:
            # Regular users get role-based permissions
            user_roles = UserRole.objects.filter(user=user)
            permissions_list = set()
            for user_role in user_roles:
                role_permissions = user_role.role.permissions.all()
                permissions_list.update([perm.name for perm in role_permissions])
            permissions_list = list(permissions_list)
        
        # Log successful login
        log_action(user, 'LOGIN', 'User', str(user.id), 'User logged in successfully', request)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'permissions': permissions_list
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log logout
        if request.user and request.user.is_authenticated:
            log_action(request.user, 'LOGOUT', 'User', str(request.user.id), 'User logged out', request)
        
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response({'message': 'Logged out successfully'})

@api_view(['GET'])
def current_user(request):
    user = request.user
    # Get user permissions
    if user.is_superuser:
        # Superusers get all permissions
        from roles.models import Permission
        all_permissions = Permission.objects.all()
        permissions_list = [perm.name for perm in all_permissions]
    else:
        # Regular users get role-based permissions
        user_roles = UserRole.objects.filter(user=user)
        permissions_list = set()
        for user_role in user_roles:
            role_permissions = user_role.role.permissions.all()
            permissions_list.update([perm.name for perm in role_permissions])
        permissions_list = list(permissions_list)
    
    return Response({
        'user': UserSerializer(user).data,
        'permissions': permissions_list
    })