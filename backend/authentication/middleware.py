from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import time


class RateLimitMiddleware:
    """
    Rate limiting middleware for login attempts.
    Limits failed login attempts to prevent brute-force attacks.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuration
        self.max_attempts = 5  # Maximum failed attempts
        self.lockout_duration = 300  # Lockout duration  (5 minutes)
        self.attempt_window = 300  # Time window for counting attempts (5 minutes)
    
    def __call__(self, request):
        # Only apply rate limiting to login endpoint
        if request.path == '/api/auth/login/' and request.method == 'POST':
            # Get client IP
            ip_address = self.get_client_ip(request)
            cache_key = f'login_attempts_{ip_address}'
            lockout_key = f'login_lockout_{ip_address}'
            
            # Check if IP is locked out
            if cache.get(lockout_key):
                return JsonResponse({
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Too many failed login attempts. Please try again later.',
                        'retry_after': cache.ttl(lockout_key)
                    }
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Get current attempts
            attempts = cache.get(cache_key, [])
            current_time = time.time()
            
            # Filter attempts within the time window
            recent_attempts = [
                attempt for attempt in attempts 
                if current_time - attempt < self.attempt_window
            ]
            
            # Check if max attempts exceeded
            if len(recent_attempts) >= self.max_attempts:
                # Lock out the IP
                cache.set(lockout_key, True, self.lockout_duration)
                return JsonResponse({
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Too many failed login attempts. Please try again later.',
                        'retry_after': self.lockout_duration
                    }
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        response = self.get_response(request)
        
        # Track failed login attempts
        if (request.path == '/api/auth/login/' and 
            request.method == 'POST' and 
            response.status_code in [400, 401]):
            
            ip_address = self.get_client_ip(request)
            cache_key = f'login_attempts_{ip_address}'
            
            attempts = cache.get(cache_key, [])
            attempts.append(time.time())
            cache.set(cache_key, attempts, self.attempt_window)
        
        # Clear attempts on successful login
        elif (request.path == '/api/auth/login/' and 
              request.method == 'POST' and 
              response.status_code == 200):
            
            ip_address = self.get_client_ip(request)
            cache_key = f'login_attempts_{ip_address}'
            cache.delete(cache_key)
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
