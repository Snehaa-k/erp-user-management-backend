from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import AuditLog
from .serializers import AuditLogSerializer
from .filters import AuditLogFilter
from companies.permissions import HasPermission
from companies.mixins import CompanyIsolationMixin

class AuditLogViewSet(CompanyIsolationMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, HasPermission('VIEW_AUDIT_LOGS')]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AuditLogFilter
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return AuditLog.objects.all()
        elif hasattr(self.request.user, 'company') and self.request.user.company:
            return AuditLog.objects.filter(company=self.request.user.company)
        else:
            return AuditLog.objects.none()