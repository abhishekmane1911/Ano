from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from .tasks import moderate_message_async


@receiver(post_save, sender=Message)
def moderate_new_message(sender, instance, created, **kwargs):
    """Trigger moderation for new messages"""
    if created and not instance.is_deleted:
        moderate_message_async.delay(instance.id)