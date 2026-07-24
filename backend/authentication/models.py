import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def validate_iiti_email(email):
    """Validate that email domain is @iiti.ac.in"""
    if not email.endswith('@iiti.ac.in'):
        raise ValidationError('Email must be from @iiti.ac.in domain')


class User(AbstractUser):
    """Custom User model with IIT Indore email validation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        validators=[validate_iiti_email],
        help_text='Must be an @iiti.ac.in email address'
    )
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['verification_token']),
            models.Index(fields=['password_reset_token']),
        ]
    
    def __str__(self):
        return self.email
    
    def generate_password_reset_token(self):
        """Generate a new password reset token"""
        self.password_reset_token = uuid.uuid4()
        self.password_reset_token_created = timezone.now()
        self.save()
        return self.password_reset_token
    
    def is_password_reset_token_valid(self):
        """Check if password reset token is still valid (1 hour expiry)"""
        if not self.password_reset_token or not self.password_reset_token_created:
            return False
        
        expiry_time = self.password_reset_token_created + timedelta(hours=1)
        return timezone.now() < expiry_time
    
    def clear_password_reset_token(self):
        """Clear password reset token after use"""
        self.password_reset_token = None
        self.password_reset_token_created = None
        self.save()
