"""
Signal handlers for security module.
Automatically creates hashed identities for new users.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import HashedIdentity
from .services import IdentityHasher

User = get_user_model()
logger = logging.getLogger('ano_platform.security')


@receiver(post_save, sender=User)
def create_hashed_identity(sender, instance, created, **kwargs):
    """
    Automatically create hashed identity when a new user is created.
    This ensures all new users have hashed identities from the start.
    """
    if created:
        try:
            # Check if hashed identity already exists
            if hasattr(instance, 'hashed_identity') and instance.hashed_identity:
                return
            
            # Create hashed identity
            email_hash, salt = IdentityHasher.hash_email(instance.email)
            HashedIdentity.objects.create(
                user=instance,
                email_hash=email_hash,
                salt=salt
            )
            logger.info(f"Created hashed identity for new user_{instance.id}")
            
        except Exception as e:
            logger.error(f"Failed to create hashed identity for user_{instance.id}: {e}")
            # Don't fail user creation if hashing fails