

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from django.utils import timezone

class PresignedURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if isinstance(request, HttpRequest) or isinstance(request, WSGIRequest):
            # Check if the request is for a presigned URL and modify its expiration time
            if 'presigned-url' in request.path:
                # Add your custom logic to modify expiration time here
                expiration_time = timezone.now() + timezone.timedelta(hours=99999)  # Example: 1 hour expiration
                request.expiration_time = expiration_time  # Add expiration time to request
        response = self.get_response(request)
        return response

