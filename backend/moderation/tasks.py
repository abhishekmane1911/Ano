from celery import shared_task
import logging
from django.utils import timezone
from datetime import timedelta
from chat.models import Message
from .services import ModerationService, HeatSystem
from .models import ModerationResult

logger = logging.getLogger('ano_platform')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def moderate_message_async(self, message_id):
    """Asynchronously moderate a message with retry logic"""
    try:
        message = Message.objects.get(id=message_id)
        result = ModerationService.moderate_content(message)
        
        # If message was rejected, mark it as deleted
        if result.action_taken == 'rejected':
            message.is_deleted = True
            message.save()
        
        logger.info(f"Moderated message {message_id}: {result.action_taken}")
        return {
            'message_id': message_id,
            'action_taken': result.action_taken,
            'toxicity_score': result.toxicity_score
        }
        
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found for moderation")
        return None
    except Exception as exc:
        logger.error(f"Error moderating message {message_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def cleanup_expired_shadowbans(self):
    """Clean up expired shadowbans with retry logic"""
    try:
        from .models import Shadowban
        
        expired_bans = Shadowban.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        
        count = expired_bans.count()
        expired_bans.update(is_active=False)
        
        logger.info(f"Cleaned up {count} expired shadowbans")
        return count
        
    except Exception as exc:
        logger.error(f"Error cleaning up shadowbans: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def update_user_heat_scores(self):
    """Update heat scores for users with violations and process rehabilitation"""
    try:
        from .models import ViolationHistory
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Mark old violations as inactive (natural decay)
        old_violations = ViolationHistory.objects.filter(
            is_active=True,
            created_at__lt=timezone.now() - timedelta(days=30)
        )
        
        count = old_violations.count()
        old_violations.update(is_active=False)
        
        # Process rehabilitation for eligible users
        rehabilitation_count = 0
        users_with_violations = User.objects.filter(
            violations__is_active=True
        ).distinct()
        
        for user in users_with_violations:
            try:
                heat_info = HeatSystem.get_heat_info(user)
                if heat_info['can_rehabilitate']:
                    if HeatSystem.attempt_rehabilitation(user):
                        rehabilitation_count += 1
                        logger.info(f"Rehabilitated user {user.id}")
            except Exception as e:
                logger.error(f"Error processing rehabilitation for user {user.id}: {e}")
                continue
        
        logger.info(f"Heat score update complete - Deactivated {count} old violations, "
                   f"Rehabilitated {rehabilitation_count} users")
        
        return {
            'deactivated_violations': count,
            'rehabilitated_users': rehabilitation_count
        }
        
    except Exception as exc:
        logger.error(f"Error updating heat scores: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def process_moderation_queue(self):
    """Process pending moderation requests with retry logic"""
    try:
        # Find messages that need re-moderation (failed previous attempts)
        recent_failed = ModerationResult.objects.filter(
            action_taken='approved',
            toxicity_score=0.0,  # Likely failed moderation
            processed_at__gte=timezone.now() - timedelta(hours=1)
        )
        
        reprocessed = 0
        for result in recent_failed:
            try:
                # Re-moderate the message
                if hasattr(result, 'message') and result.message:
                    new_result = ModerationService.moderate_content(result.message)
                    if new_result and new_result.toxicity_score > 0.0:  # Successfully processed
                        reprocessed += 1
            except Exception as e:
                logger.error(f"Error reprocessing moderation result {result.id}: {e}")
                continue
        
        logger.info(f"Reprocessed {reprocessed} failed moderation attempts")
        return reprocessed
        
    except Exception as exc:
        logger.error(f"Error processing moderation queue: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def generate_heat_report(self):
    """Generate heat system report for monitoring"""
    try:
        from django.contrib.auth import get_user_model
        from .models import ViolationHistory, Shadowban
        
        User = get_user_model()
        
        # Get statistics
        total_users = User.objects.count()
        users_with_violations = User.objects.filter(
            violations__is_active=True
        ).distinct().count()
        
        active_shadowbans = Shadowban.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        recent_violations = ViolationHistory.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Heat level distribution
        heat_distribution = {}
        for level in range(6):
            heat_distribution[level] = 0
        
        for user in User.objects.filter(violations__is_active=True).distinct():
            try:
                heat_level = HeatSystem.get_user_heat_level(user)
                heat_distribution[heat_level] += 1
            except Exception as e:
                logger.error(f"Error getting heat level for user {user.id}: {e}")
                continue
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'total_users': total_users,
            'users_with_violations': users_with_violations,
            'active_shadowbans': active_shadowbans,
            'recent_violations': recent_violations,
            'heat_distribution': heat_distribution,
            'violation_rate': (users_with_violations / total_users * 100) if total_users > 0 else 0
        }
        
        logger.info(f"Heat system report: {report}")
        return report
        
    except Exception as exc:
        logger.error(f"Error generating heat report: {exc}")
        raise self.retry(exc=exc)


# Additional background tasks for enhanced moderation processing

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def batch_moderate_messages(self, message_ids):
    """
    Process multiple messages for moderation in batch.
    
    Args:
        message_ids: List of message IDs to moderate
    """
    try:
        processed = 0
        failed = 0
        
        for message_id in message_ids:
            try:
                # Use the existing moderation task
                result = moderate_message_async.delay(message_id)
                processed += 1
            except Exception as e:
                logger.error(f"Error queuing moderation for message {message_id}: {e}")
                failed += 1
        
        logger.info(f"Batch moderation queued: {processed} processed, {failed} failed")
        return {
            'processed': processed,
            'failed': failed,
            'total': len(message_ids)
        }
        
    except Exception as exc:
        logger.error(f"Error in batch moderation task: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def schedule_moderation_maintenance(self):
    """Schedule periodic maintenance tasks for moderation system"""
    try:
        # Schedule cleanup tasks
        cleanup_expired_shadowbans.delay()
        update_user_heat_scores.delay()
        process_moderation_queue.delay()
        
        # Generate report (less frequent)
        if timezone.now().hour % 6 == 0:  # Every 6 hours
            generate_heat_report.delay()
        
        logger.info("Scheduled moderation maintenance tasks")
        return "Moderation maintenance tasks scheduled"
        
    except Exception as exc:
        logger.error(f"Error scheduling moderation maintenance: {exc}")
        raise self.retry(exc=exc)