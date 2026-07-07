import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    """Anonymous profile for users with UUID-based public identifier"""
    
    
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    anonymous_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text='Public anonymous identifier for this profile'
    )
    
    # Profile fields
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text='Optional bio text (max 500 characters)'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='Profile picture with anonymity filters'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
        indexes = [
            models.Index(fields=['anonymous_id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Profile {self.anonymous_id}"
