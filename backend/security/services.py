import hashlib
import secrets
import re
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import RateLimitRecord, HashedIdentity, SecurityEvent

User = get_user_model()


class RateLimitService:
    """Service for rate limiting user actions"""
    
    RATE_LIMITS = {
        'post_creation': (5, 600),  # 5 posts per 10 minutes
        'comment_creation': (20, 600),  # 20 comments per 10 minutes
        'vote_casting': (100, 3600),  # 100 votes per hour
        'login_attempt': (5, 300),  # 5 login attempts per 5 minutes
        'api_request': (1000, 3600),  # 1000 API requests per hour
    }
    
    @classmethod
    def check_rate_limit(cls, user: User, action_type: str, ip_address: str) -> bool:
        """Check if user has exceeded rate limit for action"""
        if action_type not in cls.RATE_LIMITS:
            return True  # Allow if no limit defined
        
        max_requests, time_window = cls.RATE_LIMITS[action_type]
        
        if not user or not user.is_authenticated:
            cache_key = f"rate_limit:anonymous:{ip_address}:{action_type}"
        else:
            cache_key = f"rate_limit:{user.id}:{action_type}"
        
        current_count = cache.get(cache_key, 0)
        
        if current_count >= max_requests:
            SecurityEvent.objects.create(
                user=user if user and user.is_authenticated else None,
                event_type='rate_limit_exceeded',
                severity='medium',
                description=f"Rate limit exceeded for {action_type}",
                ip_address=ip_address
            )
            return False
        
        cache.set(cache_key, current_count + 1, time_window)
        
        if user and user.is_authenticated:
            RateLimitRecord.objects.create(
                user=user,
                action_type=action_type,
                ip_address=ip_address
            )
        
        return True
    
    @classmethod
    def get_remaining_requests(cls, user: User, action_type: str) -> int:
        """Get remaining requests for user action"""
        if action_type not in cls.RATE_LIMITS:
            return float('inf')
        
        max_requests, _ = cls.RATE_LIMITS[action_type]
        
        if not user or not user.is_authenticated:
            return max_requests
        
        cache_key = f"rate_limit:{user.id}:{action_type}"
        current_count = cache.get(cache_key, 0)
        
        return max(0, max_requests - current_count)


class InputSanitizer:
    """Service for sanitizing user input"""
    
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
    ]
    
    @classmethod
    def sanitize_html(cls, content: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        if not content:
            return content
        
        for pattern in cls.XSS_PATTERNS:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        return content
    
    @classmethod
    def escape_javascript(cls, content: str) -> str:
        """Escape JavaScript in content"""
        if not content:
            return content
        
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        content = content.replace('"', '&quot;')
        content = content.replace("'", '&#x27;')
        content = content.replace('&', '&amp;')
        
        return content
    
    @classmethod
    def validate_input_length(cls, content: str, max_length: int) -> bool:
        """Validate input length"""
        return len(content) <= max_length
    
    @classmethod
    def check_for_malicious_patterns(cls, content: str, user: Optional[User], ip_address: str) -> bool:
        """Check for malicious patterns and log if found"""
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                SecurityEvent.objects.create(
                    user=user if user and user.is_authenticated else None,
                    event_type='xss_attempt',
                    severity='high',
                    description=f"XSS attempt detected: {pattern}",
                    ip_address=ip_address,
                    additional_data={'content_snippet': content[:200]}
                )
                return True
        
        return False


class IdentityHasher:
    """Service for hashing user identities"""
    
    @classmethod
    def hash_email(cls, email: str) -> tuple[str, str]:
        """Generate hash and salt for email"""
        salt = secrets.token_hex(16)
        email_hash = hashlib.sha256((email + salt).encode()).hexdigest()
        return email_hash, salt
    
    @classmethod
    def verify_email_hash(cls, email: str, email_hash: str, salt: str) -> bool:
        """Verify email against stored hash"""
        computed_hash = hashlib.sha256((email + salt).encode()).hexdigest()
        return computed_hash == email_hash
    
    @classmethod
    def get_hashed_identity(cls, user: User) -> Optional[HashedIdentity]:
        """Get hashed identity for user"""
        try:
            return user.hashed_identity
        except HashedIdentity.DoesNotExist:
            return None
    
    @classmethod
    def migrate_existing_emails(cls):
        """Migrate existing user emails to hashed format"""
        users_without_hash = User.objects.filter(hashed_identity__isnull=True)
        
        for user in users_without_hash:
            email_hash, salt = cls.hash_email(user.email)
            HashedIdentity.objects.create(
                user=user,
                email_hash=email_hash,
                salt=salt
            )