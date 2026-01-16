import os
from .models import RequestLog, BlockedIP
from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache


class IPLoggingMiddleware:
    """ Middleware to log the IP address, timestamp, and path of every incoming request """

    def __init__(self, get_response):
        self.get_response = get_response
        # Point to the GeoIP2 database that contains city and country location data for IP addresses
        # Download DB from https://cdn.jsdelivr.net/npm/geolite2-city/GeoLite2-City.mmdb.gz
        # Decompress it and put it in ip_tracking/geoip/
        geo_path = os.path.join(settings.BASE_DIR, 'ip_tracking', 'geoip', 'GeoLite2-City.mmdb')
        self.geo = GeoIP2(geo_path)


    def __call__(self, request):
        # Get the client's IP address
        ip_address = self.get_client_ip(request)

        # Check if this IP is blocked (exists in BlockedIP model)
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP has been blocked")
        
        cache_key = f"geo_{ip_address}"
        # Check if the geolocation for this IP is already cached in the past 24 hours
        geo = cache.get(cache_key)

        if not geo:
            try:
                # Get the geolocation data of the IP address
                geo = self.geo.city(ip_address)
                # Cache the location for this IP for 24 hours
                cache.set(cache_key, geo, 60 * 60 * 24)
            except Exception:
                geo = {}

        # Log the request
        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            country=geo.get("country_name"),
            city=geo.get("city"),
        )

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