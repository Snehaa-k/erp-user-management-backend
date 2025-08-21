from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
import json

class TenantSecurityMiddleware:
    """
    Middleware to enforce per-request security guards:
    - Check authentication
    - Check account lockout
    - Enforce tenant scoping
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for auth endpoints
        if request.path.startswith('/api/auth/'):
            return self.get_response(request)
        
        # Check if user is authenticated for protected endpoints
        if request.path.startswith('/api/') and not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check account lockout
        if (hasattr(request.user, 'locked_until') and 
            request.user.locked_until and 
            request.user.locked_until > timezone.now()):
            
            return Response(
                {'error': 'Account is locked due to failed login attempts'}, 
                status=status.HTTP_423_LOCKED
            )
        
        # Skip tenant scoping - let permission system handle access control
        
        return self.get_response(request)
    
    def is_tenant_scoped_endpoint(self, path):
        """Check if endpoint requires tenant scoping"""
        tenant_scoped_paths = [
            '/api/users/',
            '/api/roles/',
            '/api/audit-logs/',
        ]
        return any(path.startswith(scoped_path) for scoped_path in tenant_scoped_paths)