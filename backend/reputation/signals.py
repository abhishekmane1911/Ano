from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserReputation

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_reputation(sender, instance, created, **kwargs):
    """Create UserReputation instance when a new user is created"""
    if created:
        UserReputation.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_reputation(sender, instance, **kwargs):
    """Save UserReputation instance when user is saved"""
    if hasattr(instance, 'reputation'):
        instance.reputation.save()
    else:
        # Create reputation if it doesn't exist (for existing users)
        UserReputation.objects.get_or_create(user=instance)


@receiver(post_save, sender=UserReputation)
def handle_reputation_change(sender, instance, created, **kwargs):
    """
    Handle real-time tier updates when reputation changes.
    This ensures tier is always up-to-date when reputation score changes.
    """
    if not created:  # Only for updates, not creation
        # Force tier recalculation to ensure consistency
        old_tier = instance.rank_tier
        new_tier = instance.update_tier()
        
        # If tier changed, we could trigger additional actions here
        # like sending notifications, updating caches, etc.
        if old_tier != new_tier:
            # Log tier change for monitoring
            import logging
            logger = logging.getLogger('reputation')
            logger.info(f'User {instance.user.id} tier changed from {old_tier} to {new_tier} (score: {instance.reputation_score})')
            
            # Here we could add WebSocket notifications, email notifications, etc.
            # For now, we'll just ensure the tier is updated