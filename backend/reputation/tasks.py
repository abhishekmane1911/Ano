"""
Celery tasks for reputation system.
Handles background processing for reputation calculations, Wilson Score updates,
and tier management.
"""
import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta
from .models import UserReputation, MessageRanking, Vote
from .services import ReputationService, WilsonScoreCalculator
from chat.models import Message

# Import monitoring functionality
from ano_backend.monitoring import monitor_async_operation

logger = logging.getLogger('ano_platform')
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
@monitor_async_operation("reputation_calculation")
def calculate_user_reputation(self, user_id):
    """
    Background task to recalculate user reputation score.
    Used for batch updates and corrections.
    
    Args:
        user_id: ID of the user to recalculate reputation for
    """
    try:
        user = User.objects.get(id=user_id)
        reputation = ReputationService.get_or_create_reputation(user)
        
        # Recalculate reputation based on all votes received
        votes_received = Vote.objects.filter(message__sender__user=user)
        upvotes = votes_received.filter(vote_type='upvote').count()
        downvotes = votes_received.filter(vote_type='downvote').count()
        
        # Calculate new score based on current point system
        new_score = (upvotes * ReputationService.POINTS['post_upvote'] + 
                    downvotes * ReputationService.POINTS['post_downvote'])
        
        # Update reputation
        old_score = reputation.reputation_score
        old_tier = reputation.rank_tier
        
        reputation.reputation_score = max(0.0, new_score)  # Don't allow negative scores
        reputation.save()
        
        # Update tier
        new_tier = reputation.update_tier()
        
        logger.info(f"Recalculated reputation for user_{user_id}: "
                   f"{old_score} -> {reputation.reputation_score}, "
                   f"tier: {old_tier} -> {new_tier}")
        
        return {
            'user_id': user_id,
            'old_score': old_score,
            'new_score': reputation.reputation_score,
            'old_tier': old_tier,
            'new_tier': new_tier,
            'tier_changed': old_tier != new_tier
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for reputation calculation")
        return None
    except Exception as exc:
        logger.error(f"Error calculating reputation for user_{user_id}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
@monitor_async_operation("wilson_score_update")
def update_wilson_scores(self, message_ids=None):
    """
    Background task to update Wilson Scores for messages.
    Can process specific messages or all messages that need updates.
    
    Args:
        message_ids: List of message IDs to update, or None for all
    """
    try:
        if message_ids:
            messages = Message.objects.filter(id__in=message_ids)
            logger.info(f"Updating Wilson scores for {len(message_ids)} specific messages")
        else:
            # Update messages that have been voted on recently
            recent_cutoff = timezone.now() - timedelta(hours=1)
            messages = Message.objects.filter(
                votes__created_at__gte=recent_cutoff
            ).distinct()
            logger.info(f"Updating Wilson scores for {messages.count()} recently voted messages")
        
        updated_count = 0
        for message in messages:
            try:
                old_score = getattr(message.ranking, 'wilson_score', 0.0) if hasattr(message, 'ranking') else 0.0
                new_score = WilsonScoreCalculator.update_message_ranking(message)
                
                if abs(old_score - new_score) > 0.001:  # Only log significant changes
                    logger.debug(f"Updated Wilson score for message_{message.id}: "
                               f"{old_score:.4f} -> {new_score:.4f}")
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating Wilson score for message_{message.id}: {e}")
                continue
        
        logger.info(f"Wilson score update complete: {updated_count} messages processed")
        return {
            'processed_count': updated_count,
            'total_messages': messages.count() if not message_ids else len(message_ids)
        }
        
    except Exception as exc:
        logger.error(f"Error in Wilson score update task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
@monitor_async_operation("batch_tier_update")
def batch_tier_updates(self):
    """
    Background task to process tier updates for all users.
    Runs periodically to ensure tier consistency.
    """
    try:
        users_updated = 0
        tier_changes = 0
        
        # Process all users with reputation records
        for reputation in UserReputation.objects.select_related('user').all():
            try:
                old_tier = reputation.rank_tier
                new_tier = reputation.update_tier()
                
                if old_tier != new_tier:
                    tier_changes += 1
                    logger.info(f"Tier updated for user_{reputation.user.id}: "
                              f"{old_tier} -> {new_tier} "
                              f"(score: {reputation.reputation_score})")
                
                users_updated += 1
                
            except Exception as e:
                logger.error(f"Error updating tier for user_{reputation.user.id}: {e}")
                continue
        
        logger.info(f"Batch tier update complete: {users_updated} users processed, "
                   f"{tier_changes} tier changes")
        
        return {
            'users_processed': users_updated,
            'tier_changes': tier_changes
        }
        
    except Exception as exc:
        logger.error(f"Error in batch tier update task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def cleanup_old_votes(self):
    """
    Background task to clean up old vote records for performance.
    Removes votes older than 1 year while preserving reputation calculations.
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=365)
        
        # Count votes to be deleted
        old_votes = Vote.objects.filter(created_at__lt=cutoff_date)
        count = old_votes.count()
        
        if count > 0:
            # Delete old votes
            old_votes.delete()
            logger.info(f"Cleaned up {count} old vote records")
        else:
            logger.info("No old votes to clean up")
        
        return {'deleted_votes': count}
        
    except Exception as exc:
        logger.error(f"Error in vote cleanup task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_message_ranking_realtime(self, message_id):
    """
    Real-time task to update a single message's Wilson Score after voting.
    This is called immediately after votes are cast for responsive updates.
    
    Args:
        message_id: ID of the message to update
    """
    try:
        message = Message.objects.get(id=message_id)
        new_score = WilsonScoreCalculator.update_message_ranking(message)
        
        # Broadcast update via WebSocket
        try:
            from .websocket_utils import realtime_notifier
            
            # Get updated ranking data
            ranking = message.ranking
            ranking_data = {
                'upvotes': ranking.upvotes,
                'downvotes': ranking.downvotes,
                'total_votes': ranking.upvotes + ranking.downvotes,
                'wilson_score': round(ranking.wilson_score, 4),
                'upvote_percentage': round(
                    (ranking.upvotes / (ranking.upvotes + ranking.downvotes) * 100) 
                    if (ranking.upvotes + ranking.downvotes) > 0 else 0.0, 1
                )
            }
            
            # Broadcast to relevant channels
            chatroom_id = str(message.chatroom.id) if message.chatroom else None
            match_id = str(message.match.id) if message.match else None
            
            realtime_notifier.broadcast_ranking_update(
                message_id=str(message.id),
                ranking_data=ranking_data,
                chatroom_id=chatroom_id,
                match_id=match_id
            )
            
        except ImportError:
            # WebSocket utilities not available, skip broadcasting
            pass
        
        logger.debug(f"Real-time Wilson score update for message_{message_id}: {new_score:.4f}")
        return {'message_id': message_id, 'wilson_score': new_score}
        
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found for real-time ranking update")
        return None
    except Exception as exc:
        logger.error(f"Error in real-time ranking update for message_{message_id}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task
def generate_reputation_report():
    """
    Generate reputation system report for monitoring and analytics.
    """
    try:
        # Get reputation statistics
        total_users = User.objects.count()
        users_with_reputation = UserReputation.objects.count()
        
        # Tier distribution
        tier_distribution = {}
        for tier in ['Fresher', 'Sophomore', 'Senior', 'Campus Legend']:
            count = UserReputation.objects.filter(rank_tier=tier).count()
            tier_distribution[tier] = count
        
        # Score statistics
        reputation_stats = UserReputation.objects.aggregate(
            avg_score=models.Avg('reputation_score'),
            max_score=models.Max('reputation_score'),
            min_score=models.Min('reputation_score')
        )
        
        # Recent activity
        recent_votes = Vote.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'total_users': total_users,
            'users_with_reputation': users_with_reputation,
            'tier_distribution': tier_distribution,
            'reputation_stats': reputation_stats,
            'recent_votes_7d': recent_votes,
            'participation_rate': (users_with_reputation / total_users * 100) if total_users > 0 else 0
        }
        
        logger.info(f"Reputation system report: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating reputation report: {e}")
        return None


# Periodic task scheduling helpers
@shared_task
def schedule_wilson_score_updates():
    """Schedule Wilson score updates for messages with recent activity"""
    # Find messages with votes in the last hour
    recent_cutoff = timezone.now() - timedelta(hours=1)
    message_ids = list(
        Vote.objects.filter(created_at__gte=recent_cutoff)
        .values_list('message_id', flat=True)
        .distinct()
    )
    
    if message_ids:
        update_wilson_scores.delay(message_ids)
        logger.info(f"Scheduled Wilson score updates for {len(message_ids)} messages")
    
    return len(message_ids)


@shared_task
def schedule_reputation_maintenance():
    """Schedule maintenance tasks for reputation system"""
    # Schedule tier updates
    batch_tier_updates.delay()
    
    # Schedule cleanup (less frequent)
    if timezone.now().hour == 2:  # Run at 2 AM
        cleanup_old_votes.delay()
    
    logger.info("Scheduled reputation maintenance tasks")
    return "Maintenance tasks scheduled"