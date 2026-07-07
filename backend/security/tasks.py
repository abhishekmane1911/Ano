"""
Celery tasks for security system.
Handles background processing for security monitoring, rate limit cleanup,
and identity hashing operations.
"""
import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from .models import RateLimitRecord, SecurityEvent, HashedIdentity
from .services import IdentityHasher, RateLimitService

logger = logging.getLogger('ano_platform')
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_rate_limit_records(self):
    """
    Background task to clean up old rate limit records.
    Removes records older than 24 hours to maintain performance.
    """
    try:
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        # Count records to be deleted
        old_records = RateLimitRecord.objects.filter(timestamp__lt=cutoff_time)
        count = old_records.count()
        
        if count > 0:
            # Delete old records
            old_records.delete()
            logger.info(f"Cleaned up {count} old rate limit records")
        else:
            logger.info("No old rate limit records to clean up")
        
        return {'deleted_records': count}
        
    except Exception as exc:
        logger.error(f"Error in rate limit cleanup task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def migrate_user_emails_to_hash(self, batch_size=100):
    """
    Background task to migrate existing user emails to hashed format.
    Processes users in batches to avoid overwhelming the system.
    
    Args:
        batch_size: Number of users to process in each batch
    """
    try:
        # Find users without hashed identities
        users_without_hash = User.objects.filter(
            hashed_identity__isnull=True
        )[:batch_size]
        
        migrated_count = 0
        
        for user in users_without_hash:
            try:
                # Generate hash for user's email
                email_hash, salt = IdentityHasher.hash_email(user.email)
                
                # Create hashed identity record
                HashedIdentity.objects.create(
                    user=user,
                    email_hash=email_hash,
                    salt=salt
                )
                
                migrated_count += 1
                logger.debug(f"Migrated email hash for user_{user.id}")
                
            except Exception as e:
                logger.error(f"Error migrating email hash for user_{user.id}: {e}")
                continue
        
        # Check if more users need migration
        remaining_users = User.objects.filter(hashed_identity__isnull=True).count()
        
        logger.info(f"Email hash migration batch complete: {migrated_count} users migrated, "
                   f"{remaining_users} remaining")
        
        # Schedule next batch if needed
        if remaining_users > 0:
            migrate_user_emails_to_hash.apply_async(
                args=[batch_size],
                countdown=60  # Wait 1 minute before next batch
            )
        
        return {
            'migrated_count': migrated_count,
            'remaining_users': remaining_users,
            'batch_complete': remaining_users == 0
        }
        
    except Exception as exc:
        logger.error(f"Error in email hash migration task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def analyze_security_events(self):
    """
    Background task to analyze security events and detect patterns.
    Identifies potential security threats and suspicious activity.
    """
    try:
        # Analyze events from the last 24 hours
        cutoff_time = timezone.now() - timedelta(hours=24)
        recent_events = SecurityEvent.objects.filter(created_at__gte=cutoff_time)
        
        # Count events by type
        event_counts = {}
        for event in recent_events:
            event_type = event.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Identify suspicious patterns
        suspicious_patterns = []
        
        # High rate limit violations
        if event_counts.get('rate_limit_exceeded', 0) > 100:
            suspicious_patterns.append({
                'type': 'high_rate_limit_violations',
                'count': event_counts['rate_limit_exceeded'],
                'severity': 'medium'
            })
        
        # Multiple XSS attempts
        if event_counts.get('xss_attempt', 0) > 10:
            suspicious_patterns.append({
                'type': 'multiple_xss_attempts',
                'count': event_counts['xss_attempt'],
                'severity': 'high'
            })
        
        # Analyze by IP address
        ip_analysis = {}
        for event in recent_events.filter(severity__in=['high', 'critical']):
            ip = event.ip_address
            if ip:
                if ip not in ip_analysis:
                    ip_analysis[ip] = {'count': 0, 'events': []}
                ip_analysis[ip]['count'] += 1
                ip_analysis[ip]['events'].append(event.event_type)
        
        # Flag IPs with multiple high-severity events
        suspicious_ips = []
        for ip, data in ip_analysis.items():
            if data['count'] >= 5:  # 5 or more high-severity events
                suspicious_ips.append({
                    'ip_address': ip,
                    'event_count': data['count'],
                    'event_types': list(set(data['events']))
                })
        
        # Log analysis results
        if suspicious_patterns or suspicious_ips:
            logger.warning(f"Security analysis found {len(suspicious_patterns)} patterns "
                         f"and {len(suspicious_ips)} suspicious IPs")
            
            # Create summary security event
            SecurityEvent.objects.create(
                event_type='security_analysis',
                severity='medium',
                description=f"Security analysis completed: {len(suspicious_patterns)} patterns, "
                           f"{len(suspicious_ips)} suspicious IPs",
                additional_data={
                    'suspicious_patterns': suspicious_patterns,
                    'suspicious_ips': suspicious_ips,
                    'event_counts': event_counts
                }
            )
        
        return {
            'total_events': recent_events.count(),
            'event_counts': event_counts,
            'suspicious_patterns': suspicious_patterns,
            'suspicious_ips': suspicious_ips
        }
        
    except Exception as exc:
        logger.error(f"Error in security analysis task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_security_events(self):
    """
    Background task to clean up old security events.
    Removes events older than 30 days while preserving critical events.
    """
    try:
        cutoff_time = timezone.now() - timedelta(days=30)
        
        # Keep critical events longer (90 days)
        critical_cutoff = timezone.now() - timedelta(days=90)
        
        # Delete old non-critical events
        old_events = SecurityEvent.objects.filter(
            timestamp__lt=cutoff_time
        ).exclude(severity='critical')

        # Delete very old critical events
        old_critical_events = SecurityEvent.objects.filter(
            timestamp__lt=critical_cutoff,
            severity='critical'
        )
        
        regular_count = old_events.count()
        critical_count = old_critical_events.count()
        
        if regular_count > 0:
            old_events.delete()
            logger.info(f"Cleaned up {regular_count} old security events")
        
        if critical_count > 0:
            old_critical_events.delete()
            logger.info(f"Cleaned up {critical_count} old critical security events")
        
        return {
            'deleted_regular': regular_count,
            'deleted_critical': critical_count,
            'total_deleted': regular_count + critical_count
        }
        
    except Exception as exc:
        logger.error(f"Error in security events cleanup task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=180)
def reset_rate_limit_cache(self, user_id=None, action_type=None):
    """
    Background task to reset rate limit cache entries.
    Can reset for specific user/action or clear all rate limit cache.
    
    Args:
        user_id: Specific user ID to reset (optional)
        action_type: Specific action type to reset (optional)
    """
    try:
        reset_count = 0
        
        if user_id and action_type:
            # Reset specific user/action combination
            cache_key = f"rate_limit:{user_id}:{action_type}"
            if cache.delete(cache_key):
                reset_count = 1
                logger.info(f"Reset rate limit cache for user_{user_id}, action: {action_type}")
        
        elif user_id:
            # Reset all actions for specific user
            for action in RateLimitService.RATE_LIMITS.keys():
                cache_key = f"rate_limit:{user_id}:{action}"
                if cache.delete(cache_key):
                    reset_count += 1
            logger.info(f"Reset all rate limit cache entries for user_{user_id}")
        
        elif action_type:
            # Reset specific action for all users (more complex, not implemented)
            logger.warning("Resetting action type for all users not implemented")
        
        else:
            # Clear all rate limit cache (use with caution)
            # This would require iterating through all possible keys
            logger.warning("Full rate limit cache reset not implemented for safety")
        
        return {'reset_count': reset_count}
        
    except Exception as exc:
        logger.error(f"Error in rate limit cache reset task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task
def generate_security_report():
    """
    Generate security system report for monitoring and compliance.
    """
    try:
        # Get security statistics for the last 24 hours
        cutoff_time = timezone.now() - timedelta(hours=24)
        recent_events = SecurityEvent.objects.filter(created_at__gte=cutoff_time)
        
        # Count events by severity
        severity_counts = {}
        for severity in ['low', 'medium', 'high', 'critical']:
            count = recent_events.filter(severity=severity).count()
            severity_counts[severity] = count
        
        # Count events by type
        event_type_counts = {}
        for event in recent_events:
            event_type = event.event_type
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        # Rate limiting statistics
        recent_rate_limits = RateLimitRecord.objects.filter(
            timestamp__gte=cutoff_time
        )
        
        rate_limit_stats = {}
        for record in recent_rate_limits:
            action = record.action_type
            rate_limit_stats[action] = rate_limit_stats.get(action, 0) + 1
        
        # Identity hashing progress
        total_users = User.objects.count()
        hashed_users = HashedIdentity.objects.count()
        hashing_progress = (hashed_users / total_users * 100) if total_users > 0 else 0
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'period': '24_hours',
            'total_security_events': recent_events.count(),
            'severity_distribution': severity_counts,
            'event_type_distribution': event_type_counts,
            'rate_limit_activity': rate_limit_stats,
            'identity_hashing': {
                'total_users': total_users,
                'hashed_users': hashed_users,
                'progress_percentage': round(hashing_progress, 2)
            },
            'system_health': {
                'high_severity_events': severity_counts.get('high', 0) + severity_counts.get('critical', 0),
                'rate_limit_violations': event_type_counts.get('rate_limit_exceeded', 0),
                'xss_attempts': event_type_counts.get('xss_attempt', 0)
            }
        }
        
        logger.info(f"Security system report: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating security report: {e}")
        return None


# Periodic task scheduling helpers
@shared_task
def schedule_security_maintenance():
    """Schedule maintenance tasks for security system"""
    # Schedule daily cleanup tasks
    cleanup_rate_limit_records.delay()
    
    # Schedule security analysis
    analyze_security_events.delay()
    
    # Schedule weekly cleanup (run on Sundays)
    if timezone.now().weekday() == 6:  # Sunday
        cleanup_security_events.delay()
    
    # Continue email hash migration if needed
    remaining_users = User.objects.filter(hashed_identity__isnull=True).count()
    if remaining_users > 0:
        migrate_user_emails_to_hash.delay()
    
    logger.info("Scheduled security maintenance tasks")
    return "Security maintenance tasks scheduled"


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def emergency_security_lockdown(self, reason="Manual trigger"):
    """
    Emergency task to implement security lockdown measures.
    Increases rate limits and enables additional security measures.
    """
    try:
        # Log the lockdown event
        SecurityEvent.objects.create(
            event_type='emergency_lockdown',
            severity='critical',
            description=f"Emergency security lockdown activated: {reason}",
            additional_data={'reason': reason, 'timestamp': timezone.now().isoformat()}
        )
        
        # Implement lockdown measures (this would be customized based on needs)
        lockdown_measures = {
            'rate_limits_tightened': True,
            'additional_logging_enabled': True,
            'lockdown_reason': reason,
            'lockdown_time': timezone.now().isoformat()
        }
        
        # Store lockdown state in cache
        cache.set('security_lockdown_active', lockdown_measures, timeout=3600)  # 1 hour
        
        logger.critical(f"Emergency security lockdown activated: {reason}")
        return lockdown_measures
        
    except Exception as exc:
        logger.error(f"Error in emergency lockdown task: {str(exc)}")
        raise self.retry(exc=exc)