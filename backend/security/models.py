import hashlib
import secrets
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class RateLimitRecord(models.Model):
    """Track user actions for rate limiting"""
    
    ACTION_TYPES = [
        ('post_creation', 'Post Creation'),
        ('comment_creation', 'Comment Creation'),
        ('vote_casting', 'Vote Casting'),
        ('login_attempt', 'Login Attempt'),
        ('api_request', 'API Request'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rate_limit_records')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    
    class Meta:
        db_table = 'rate_limit_records'
        indexes = [
            models.Index(fields=['user', 'action_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.action_type} at {self.timestamp}"


class HashedIdentity(models.Model):
    """Store hashed email identities for enhanced privacy"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hashed_identity')
    email_hash = models.CharField(max_length=64, unique=True)
    salt = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hashed_identities'
        indexes = [
            models.Index(fields=['email_hash']),
        ]
    
    def __str__(self):
        return f"Hashed identity for {self.user.email}"
    
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


class SecurityEvent(models.Model):
    """Log security-related events"""
    
    EVENT_TYPES = [
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('failed_authentication', 'Failed Authentication'),
        ('xss_attempt', 'XSS Attempt'),
        ('csrf_failure', 'CSRF Failure'),
        ('input_sanitization', 'Input Sanitization'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    additional_data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_events'
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.severity} at {self.timestamp}"
