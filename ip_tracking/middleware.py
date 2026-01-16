from .models import RequestLog, BlockedIP
from django.http import HttpResponseForbidden


class IPLoggingMiddleware:
    """ Middleware to log the IP address, timestamp, and path of every incoming request """

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        # Get the client's IP address
        ip_address = self.get_client_ip(request)

        # Check if this IP is blocked (exists in BlockedIP model)
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP has been blocked")

        # Log the request
        RequestLog.objects.create(ip_address=ip_address, path=request.path)

        response = self.get_response(request)
        return response


    def get_client_ip(self, request):
        """ Retrieve the client's IP address from the request """
        # Check for X-Forwarded-For header first (in case of proxy in production)
        # x_forwarded_for will look like: "client_ip, proxy1_ip, proxy2_ip"
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:  # In production, behind a proxy
            ip = x_forwarded_for.split(',')[0]
        else:  # Direct request in local development
            ip = request.META.get('REMOTE_ADDR')
        return ip