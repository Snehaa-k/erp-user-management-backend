from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Role, Permission, UserRole
from .serializers import RoleSerializer, RoleCreateUpdateSerializer, PermissionSerializer, AssignPermissionsSerializer
from companies.permissions import HasPermission
from companies.mixins import CompanyIsolationMixin
from audit.utils import log_action

class RoleViewSet(CompanyIsolationMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # All users can see all roles (system-wide roles)
        return Role.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RoleCreateUpdateSerializer
        return RoleSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated, HasPermission('VIEW_ROLES')]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, HasPermission('CREATE_ROLE')]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, HasPermission('UPDATE_ROLE')]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, HasPermission('DELETE_ROLE')]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        role = serializer.save()
        log_action(self.request.user, 'CREATE', 'Role', str(role.id), f'Created role: {role.name}', self.request)
    
    def perform_update(self, serializer):
        role = serializer.save()
        log_action(self.request.user, 'UPDATE', 'Role', str(role.id), f'Updated role: {role.name}', self.request)
    
    def perform_destroy(self, instance):
        log_action(self.request.user, 'DELETE', 'Role', str(instance.id), f'Deleted role: {instance.name}', self.request)
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, HasPermission('ASSIGN_PERMISSIONS')])
    def assign_permissions(self, request, pk=None):
        role = self.get_object()
        serializer = AssignPermissionsSerializer(data=request.data)
        
        if serializer.is_valid():
            permission_names = serializer.validated_data['permissions']
            permissions_objs = Permission.objects.filter(name__in=permission_names)
            role.permissions.set(permissions_objs)
            
            log_action(request.user, 'UPDATE', 'Role', str(role.id), f'Updated permissions for role: {role.name}', request)
            
            return Response({'message': 'Permissions assigned successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission('VIEW_PERMISSIONS')]