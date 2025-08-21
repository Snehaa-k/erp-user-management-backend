from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company, User
from .serializers import CompanySerializer, UserListSerializer, UserCreateUpdateSerializer
from .mixins import CompanyIsolationMixin
from roles.models import UserRole, Role
from audit.utils import log_action
from .permissions import HasPermission

class CompanyViewSet(CompanyIsolationMixin, viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Super admin can see all companies
        if self.request.user.is_superuser:
            return Company.objects.all()
        # Users with company see only their own
        elif hasattr(self.request.user, 'company') and self.request.user.company:
            return Company.objects.filter(id=self.request.user.company.id)
        # Users without company but with VIEW_COMPANIES permission can see all
        else:
            return Company.objects.all()
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated, HasPermission('VIEW_COMPANIES')]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, HasPermission('CREATE_COMPANY')]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, HasPermission('UPDATE_COMPANY')]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, HasPermission('DELETE_COMPANY')]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        company = serializer.save()
        log_action(self.request.user, 'CREATE', 'Company', str(company.id), f'Created company: {company.name}', self.request)
    
    def perform_update(self, serializer):
        company = serializer.save()
        log_action(self.request.user, 'UPDATE', 'Company', str(company.id), f'Updated company: {company.name}', self.request)
    
    def perform_destroy(self, instance):
        log_action(self.request.user, 'DELETE', 'Company', str(instance.id), f'Deleted company: {instance.name}', self.request)
        instance.delete()

class UserViewSet(CompanyIsolationMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Superusers can see all users
        if self.request.user.is_superuser:
            return User.objects.all()
        # Users with company see only their company users
        elif hasattr(self.request.user, 'company') and self.request.user.company:
            return User.objects.filter(company=self.request.user.company)
        # Users without company but with VIEW_USERS permission can see all
        else:
            return User.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserListSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated, HasPermission('VIEW_USERS')]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, HasPermission('CREATE_USER')]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, HasPermission('UPDATE_USER')]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, HasPermission('DELETE_USER')]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        user = serializer.save()
        log_action(self.request.user, 'CREATE', 'User', str(user.id), f'Created user', self.request)
    
    def perform_update(self, serializer):
        user = serializer.save()
        log_action(self.request.user, 'UPDATE', 'User', str(user.id), f'Updated user: {user.username}', self.request)
    
    def perform_destroy(self, instance):
        log_action(self.request.user, 'DELETE', 'User', str(instance.id), f'Deleted user: {instance.username}', self.request)
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def assign_company(self, request, pk=None):
        """Assign company to user (superuser only)"""
        if not request.user.is_superuser:
            return Response({'error': 'Only superusers can assign companies'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        company_id = request.data.get('company_id')
        
        try:
            from companies.models import Company
            company = Company.objects.get(id=company_id)
            user.company = company
            user.save()
            
            log_action(request.user, 'UPDATE', 'User', str(user.id), f'Assigned company {company.name} to user {user.username}', request)
            return Response({'message': 'Company assigned successfully'})
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def assign_role(self, request, pk=None):
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        # Check permissions
        if not request.user.is_superuser and not hasPermission('ASSIGN_ROLES'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Get role (roles are system-wide now)
            role = Role.objects.get(id=role_id)
            
            user_role, created = UserRole.objects.get_or_create(user=user, role=role)
            
            if created:
                log_action(request.user, 'UPDATE', 'UserRole', str(user_role.id), f'Assigned role {role.name} to user {user.username}', request)
                
                # Send real-time notification
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    # Get updated permissions
                    user_roles = UserRole.objects.filter(user=user)
                    permissions = set()
                    for ur in user_roles:
                        role_permissions = ur.role.permissions.all()
                        permissions.update([perm.name for perm in role_permissions])
                    
                    async_to_sync(channel_layer.group_send)(
                        f"user_{user.id}",
                        {
                            "type": "permission_update",
                            "user_id": user.id,
                            "permissions": list(permissions)
                        }
                    )
                
                return Response({'message': 'Role assigned successfully'})
            else:
                return Response({'message': 'Role already assigned'})
        except Role.DoesNotExist:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated, HasPermission('ASSIGN_ROLES')])
    def remove_role(self, request, pk=None):
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        try:
            # Get role (roles are system-wide now)
            role = Role.objects.get(id=role_id)
            
            user_role = UserRole.objects.filter(user=user, role=role).first()
            
            if user_role:
                user_role.delete()
                log_action(request.user, 'UPDATE', 'UserRole', str(user_role.id), f'Removed role {role.name} from user {user.username}', request)
                
                # Send real-time notification
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    # Get updated permissions
                    user_roles = UserRole.objects.filter(user=user)
                    permissions = set()
                    for ur in user_roles:
                        role_permissions = ur.role.permissions.all()
                        permissions.update([perm.name for perm in role_permissions])
                    
                    async_to_sync(channel_layer.group_send)(
                        f"user_{user.id}",
                        {
                            "type": "permission_update",
                            "user_id": user.id,
                            "permissions": list(permissions)
                        }
                    )
                
                return Response({'message': 'Role removed successfully'})
            else:
                return Response({'message': 'Role not assigned to user'})
        except Role.DoesNotExist:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)