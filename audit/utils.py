from .models import AuditLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(user, action, resource_type, resource_id, details, request=None):
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    if not user:
        return
    
    # For superusers, use None for company (system-level actions)
    company = None
    if hasattr(user, 'company') and user.company:
        company = user.company
    
    AuditLog.objects.create(
        user=user,
        company=company,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address or 'unknown',
        user_agent=user_agent or 'unknown'
    )