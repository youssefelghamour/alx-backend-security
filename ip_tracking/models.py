from django.db import models


class RequestLog(models.Model):
    """Model to log incoming requests with IP address and timestamp"""
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.ip_address} - {self.timestamp}"


class BlockedIP(models.Model):
    """Model to store blocked IP addresses"""
    ip_address = models.GenericIPAddressField(unique=True)

    def __str__(self):
        return self.ip_address