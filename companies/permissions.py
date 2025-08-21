from rest_framework import permissions
from roles.models import UserRole

def HasPermission(required_permission):
    class PermissionClass(permissions.BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            
            if request.user.is_superuser:
                return True
            
            # Get user permissions regardless of company assignment
            user_roles = UserRole.objects.filter(user=request.user)
            user_permissions = set()
            for user_role in user_roles:
                role_permissions = user_role.role.permissions.all()
                user_permissions.update([perm.name for perm in role_permissions])
            
            return required_permission in user_permissions
            

    
    return PermissionClass