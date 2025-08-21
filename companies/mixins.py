from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class CompanyIsolationMixin:
    """
    Mixin to enforce strict data isolation based on user's company.
    Ensures users can only access data within their assigned company.
    """
    
    def get_queryset(self):
        """Filter queryset to only include data from user's company"""
        queryset = super().get_queryset()
        
        # Superusers can access all data across all companies
        if self.request.user.is_superuser:
            return queryset
        
        # Regular users can only access their company's data
        if hasattr(self.request.user, 'company') and self.request.user.company:
            if hasattr(queryset.model, 'company'):
                return queryset.filter(company=self.request.user.company)
            else:
                return queryset.none()
        
        # Users without company get no data
        return queryset.none()
    
    def perform_create(self, serializer):
        """Ensure created objects belong to appropriate company"""
        # Superusers can create for any company (handled in serializer)
        if self.request.user.is_superuser:
            serializer.save()
        else:
            # Regular users can only create for their company
            if hasattr(self.request.user, 'company') and self.request.user.company:
                serializer.save(company=self.request.user.company)
            else:
                raise PermissionDenied("User must belong to a company")
    
    def get_object(self):
        """Ensure retrieved object belongs to user's company"""
        obj = super().get_object()
        
        # Superusers can access any object across all companies
        if self.request.user.is_superuser:
            return obj
        
        # Check if object belongs to user's company
        if hasattr(obj, 'company'):
            if hasattr(self.request.user, 'company') and self.request.user.company:
                if obj.company != self.request.user.company:
                    raise PermissionDenied("Access denied: Object belongs to different company")
            else:
                raise PermissionDenied("User must belong to a company")
        
        return obj