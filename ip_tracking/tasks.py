from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP


@shared_task
def detect_anomalies():
    """Celery task to detect and to flag suspicious IPs:
        - High volume (>100 requests/hour)
        - Access to sensitive paths (/admin, /login)
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    ##### 1. Flag high volume

    # List of IPs with more than 100 requests in the last hour
    high_volume_ips = RequestLog.objects.filter(timestamp__gte=one_hour_ago).values('ip_address').annotate(cnt=Count('id')).filter(cnt__gt=100)

    # Mark these IPs as suspicious by adding to SuspiciousIP, if not already present
    for ip in high_volume_ips:
        SuspiciousIP.objects.get_or_create(ip_address=ip['ip_address'], reason="Request volume > 100/hr")

    ##### 2. Flag sensitive path access
    sensitive_paths = ['/admin/', '/login/']

    # Get distinct IPs that accessed sensitive paths in the last hour
    sensitive_ips = RequestLog.objects.filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths).values_list('ip_address', flat=True).distinct()
    
    for ip in sensitive_ips:
        SuspiciousIP.objects.get_or_create(ip_address=ip, reason="Accessed sensitive path")