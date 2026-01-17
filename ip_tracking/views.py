from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit


@ratelimit(key='user', rate='10/m', block=False)
@ratelimit(key='ip', rate='5/m', block=False)
def login_view(request):
    """Views for login with rate limiting applied
        - User-based limit (authenticated): 10 requests per minute
        - IP-based limit (anonymous): 5 requests per minute
    """
    # Check if the request was limited to handle the Ratelimited exception manually
    # Or you can let the decorator handle it by setting block=True which stops the request automatically
    if getattr(request, 'limited', False):
        return HttpResponse("Too many requests", status=429)
    return HttpResponse("Ok")