import django_filters
from django.db.models import Q
from .models import AuditLog

class AuditLogFilter(django_filters.FilterSet):
    action = django_filters.CharFilter(field_name='action', lookup_expr='iexact')
    user = django_filters.CharFilter(method='filter_user')
    start_date = django_filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = AuditLog
        fields = ['action', 'user', 'start_date', 'end_date']
    
    def filter_user(self, queryset, name, value):
        return queryset.filter(
            Q(user__username__icontains=value) | 
            Q(user__email__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value)
        )