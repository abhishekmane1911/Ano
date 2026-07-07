import logging
from celery import shared_task
from django.utils import timezone
from .models import Message

logger = logging.getLogger(__name__)

@shared_task
def unpin_expired_messages():
    """
    Periodic task to automatically unpin messages that have exceeded their
    user-defined pin duration (pin_expires_at).
    """
    try:
        expired_messages = Message.objects.filter(
            is_pinned=True, 
            pin_expires_at__lt=timezone.now()
        )
        
        count = expired_messages.count()
        if count > 0:
            expired_messages.update(is_pinned=False, pin_expires_at=None)
            logger.info(f"Successfully unpinned {count} expired messages.")
            
        return f"Unpinned {count} messages"
    except Exception as e:
        logger.error(f"Error unpinning expired messages: {str(e)}")
        raise
