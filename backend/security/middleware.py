import logging
import json
from typing import Optional
from django.http import JsonResponse, HttpRequest
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import CsrfViewMiddleware
from .services import RateLimitService, InputSanitizer
from .models import SecurityEvent

User = get_user_model()
security_logger = logging.getLogger('ano_platform.security')


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Middleware for rate limiting user actions with configurable limits.
    Implements progressive delays and security event logging.
    """
    
    RATE_LIMITED_ACTIONS = {
        'POST': {
            '/api/chat/messages/': 'post_creation',
            '/api/chat/comments/': 'comment_creation',
            '/api/reputation/vote/': 'vote_casting',
            '/api/auth/login/': 'login_attempt',
        },
        'GET': {
            # API requests are generally rate limited
        }
    }
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Process request and check rate limits"""
        if self._should_skip_rate_limiting(request):
            return None
        
        user = getattr(request, 'user', None)
        ip_address = self._get_client_ip(request)
        
        action_type = self._get_action_type(request)
        if not action_type:
            return None
        

        if action_type != 'login_attempt' and (not user or not user.is_authenticated):
            return None
        
        if not RateLimitService.check_rate_limit(user, action_type, ip_address):
            remaining = RateLimitService.get_remaining_requests(user, action_type)
            
            security_logger.warning(
                f"Rate limit exceeded for user {user.id if user and user.is_authenticated else 'anonymous'} "
                f"on action {action_type} from IP {ip_address}"
            )
            
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Too many {action_type.replace("_", " ")} requests. Please try again later.',
                'remaining_requests': remaining,
                'retry_after': self._get_retry_after(action_type)
            }, status=429)
        
        return None
    
    def _should_skip_rate_limiting(self, request: HttpRequest) -> bool:
        """Check if rate limiting should be skipped for this request"""
        if request.path.startswith('/admin/'):
            return True
        
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return True
        
        if request.path in ['/health/', '/api/health/']:
            return True
        
        return False
    
    def _get_action_type(self, request: HttpRequest) -> Optional[str]:
        """Determine the action type based on request method and path"""
        method = request.method
        path = request.path
        
        if method in self.RATE_LIMITED_ACTIONS:
            action_mappings = self.RATE_LIMITED_ACTIONS[method]
            for endpoint, action in action_mappings.items():
                if path.startswith(endpoint):
                    return action
        
        if path.startswith('/api/'):
            return 'api_request'
        
        return None
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    def _get_retry_after(self, action_type: str) -> int:
        """Get retry after time in seconds for action type"""
        rate_limits = RateLimitService.RATE_LIMITS
        if action_type in rate_limits:
            _, time_window = rate_limits[action_type]
            return time_window
        return 3600  


class InputSanitizationMiddleware(MiddlewareMixin):
    """
    Middleware for sanitizing user input to prevent XSS attacks.
    Validates and escapes all user-generated content before processing.
    """
    
    SANITIZE_FIELDS = [
        'content', 'message', 'text', 'description', 'title', 'bio', 'comment'
    ]
    
    MAX_LENGTHS = {
        'content': 5000,
        'message': 2000,
        'text': 2000,
        'description': 1000,
        'title': 200,
        'bio': 500,
        'comment': 1000,
    }
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Process request and sanitize input"""
        if self._should_skip_sanitization(request):
            return None
        
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return None
        
        user = getattr(request, 'user', None)
        ip_address = self._get_client_ip(request)
        
        try:
            if hasattr(request, 'body') and request.body:
                if request.content_type == 'application/json':
                    data = json.loads(request.body.decode('utf-8'))
                    sanitized_data = self._sanitize_data(data, user, ip_address)
                    
                    # Replace request body with sanitized data
                    request._body = json.dumps(sanitized_data).encode('utf-8')
                    
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            security_logger.warning(
                f"Failed to parse request body for sanitization: {e} "
                f"from user {user.id if user else 'anonymous'} at IP {ip_address}"
            )
            return JsonResponse({
                'error': 'Invalid request format',
                'message': 'Request body could not be parsed'
            }, status=400)
        
        return None
    
    def _should_skip_sanitization(self, request: HttpRequest) -> bool:
        """Check if sanitization should be skipped for this request"""
        if request.path.startswith('/admin/'):
            return True
        
        if '/auth/' in request.path:
            return True
        
        if '/profiles/' in request.path:
            return True
        
        if request.content_type and request.content_type.startswith('multipart/'):
            return True
        
        if request.path in ['/health/', '/api/health/']:
            return True
        
        return False
    
    def _sanitize_data(self, data: dict, user: Optional[User], ip_address: str) -> dict:
        """Recursively sanitize data dictionary"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value, user, ip_address)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_data(item, user, ip_address) if isinstance(item, dict)
                    else self._sanitize_string(item, key, user, ip_address) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str) and key.lower() in self.SANITIZE_FIELDS:
                sanitized[key] = self._sanitize_string(value, key, user, ip_address)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_string(self, content: str, field_name: str, user: Optional[User], ip_address: str) -> str:
        """Sanitize a string field"""
        if not content:
            return content
        
        max_length = self.MAX_LENGTHS.get(field_name.lower(), 2000)
        if not InputSanitizer.validate_input_length(content, max_length):
            raise ValueError(f"Content too long for field {field_name}")
        
        if InputSanitizer.check_for_malicious_patterns(content, user, ip_address):
            security_logger.warning(
                f"Malicious pattern detected in {field_name} from user "
                f"{user.id if user else 'anonymous'} at IP {ip_address}"
            )
            return InputSanitizer.escape_javascript(content)
        
        sanitized = InputSanitizer.sanitize_html(content)
        
        sanitized = InputSanitizer.escape_javascript(sanitized)
        
        return sanitized
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class EnhancedCSRFMiddleware(CsrfViewMiddleware):
    """
    Enhanced CSRF middleware with additional security logging.
    Extends Django's built-in CSRF protection with security event logging.
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        """Process view with enhanced CSRF protection and logging"""
        result = super().process_view(request, callback, callback_args, callback_kwargs)
        
        if result is not None: 
            user = getattr(request, 'user', None)
            ip_address = self._get_client_ip(request)
            
            SecurityEvent.objects.create(
                user=user if user and user.is_authenticated else None,
                event_type='csrf_failure',
                severity='high',
                description=f'CSRF token validation failed for {request.method} {request.path}',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                additional_data={
                    'method': request.method,
                    'path': request.path,
                    'referer': request.META.get('HTTP_REFERER', ''),
                }
            )
            
            security_logger.warning(
                f"CSRF failure for user {user.id if user and user.is_authenticated else 'anonymous'} "
                f"on {request.method} {request.path} from IP {ip_address}"
            )
        
        return result
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip