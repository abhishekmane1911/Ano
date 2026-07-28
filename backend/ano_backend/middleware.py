import logging
import time
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from ano_backend.logging_config import get_anonymous_id_from_user

request_logger = logging.getLogger('ano_platform')
security_logger = logging.getLogger('ano_platform.security')


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.
    Implements Content Security Policy and other security headers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'", 
            "style-src 'self' 'unsafe-inline'", 
            "img-src 'self' data: blob: https:",  
            "font-src 'self' data:",
            "connect-src 'self' ws: wss:",  
            "media-src 'self' blob:",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests" if not settings.DEBUG else "",
        ]
        response['Content-Security-Policy'] = '; '.join(filter(None, csp_directives))
        
        # more security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class HTTPSRedirectMiddleware:
    """
    Middleware to redirect all HTTP requests to HTTPS in production.
    Only active when DEBUG is False and not in test mode.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip redirect in development, testing, or if already secure
        import sys
        is_testing = 'test' in sys.argv or hasattr(settings, 'TESTING')
        
        if not settings.DEBUG and not is_testing:
            if not request.is_secure():
                url = request.build_absolute_uri(request.get_full_path())
                secure_url = url.replace('http://', 'https://', 1)
                return HttpResponsePermanentRedirect(secure_url)
        
        return self.get_response(request)


class AnonymousLoggingMiddleware:
    """
    Middleware to log all requests using anonymous identifiers.
    Ensures no emails or real names appear in request logs.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Get anonymous identifier for the user
        anonymous_id = None
        if hasattr(request, 'user'):
            anonymous_id = get_anonymous_id_from_user(request.user)
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        log_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration': f'{duration:.3f}s',
            'anonymous_id': anonymous_id or 'anonymous',
            'ip': self._get_client_ip(request),
        }
        
        if response.status_code >= 500:
            request_logger.error(
                f"{log_data['method']} {log_data['path']} - "
                f"Status: {log_data['status']} - "
                f"Duration: {log_data['duration']} - "
                f"User: {log_data['anonymous_id']} - "
                f"IP: {log_data['ip']}"
            )
        elif response.status_code >= 400:
            request_logger.warning(
                f"{log_data['method']} {log_data['path']} - "
                f"Status: {log_data['status']} - "
                f"Duration: {log_data['duration']} - "
                f"User: {log_data['anonymous_id']} - "
                f"IP: {log_data['ip']}"
            )
        else:
            request_logger.info(
                f"{log_data['method']} {log_data['path']} - "
                f"Status: {log_data['status']} - "
                f"Duration: {log_data['duration']} - "
                f"User: {log_data['anonymous_id']}"
            )
        
        return response
    
    def _get_client_ip(self, request):
        """Extract client IP address from request, handling proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    def process_exception(self, request, exception):
        """Log exceptions with anonymous identifier."""
        anonymous_id = None
        if hasattr(request, 'user'):
            anonymous_id = get_anonymous_id_from_user(request.user)
        
        request_logger.exception(
            f"Exception in {request.method} {request.path} - "
            f"User: {anonymous_id or 'anonymous'} - "
            f"Exception: {type(exception).__name__}"
        )
        
        return None  
