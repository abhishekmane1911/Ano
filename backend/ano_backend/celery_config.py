"""
Celery configuration for advanced gamification modules.
Defines periodic tasks and beat schedule for background processing.
"""
from celery.schedules import crontab

# Celery Beat Schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    # Reputation System Tasks
    'update-wilson-scores': {
        'task': 'reputation.tasks.schedule_wilson_score_updates',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'reputation-maintenance': {
        'task': 'reputation.tasks.schedule_reputation_maintenance',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
    'batch-tier-updates': {
        'task': 'reputation.tasks.batch_tier_updates',
        'schedule': crontab(hour='*/6', minute=0),  # Every 6 hours
    },
    'reputation-report': {
        'task': 'reputation.tasks.generate_reputation_report',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    
    # Moderation System Tasks
    'moderation-maintenance': {
        'task': 'moderation.tasks.schedule_moderation_maintenance',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'cleanup-expired-shadowbans': {
        'task': 'moderation.tasks.cleanup_expired_shadowbans',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    'update-heat-scores': {
        'task': 'moderation.tasks.update_user_heat_scores',
        'schedule': crontab(hour='*/4', minute=0),  # Every 4 hours
    },
    'process-moderation-queue': {
        'task': 'moderation.tasks.process_moderation_queue',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'heat-system-report': {
        'task': 'moderation.tasks.generate_heat_report',
        'schedule': crontab(hour='*/6', minute=30),  # Every 6 hours at :30
    },
    
    # Security System Tasks
    'security-maintenance': {
        'task': 'security.tasks.schedule_security_maintenance',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-rate-limits': {
        'task': 'security.tasks.cleanup_rate_limit_records',
        'schedule': crontab(hour='*/2', minute=0),  # Every 2 hours
    },
    'security-analysis': {
        'task': 'security.tasks.analyze_security_events',
        'schedule': crontab(hour='*/4', minute=15),  # Every 4 hours at :15
    },
    'security-report': {
        'task': 'security.tasks.generate_security_report',
        'schedule': crontab(hour=0, minute=30),  # Daily at 12:30 AM
    },
    'migrate-email-hashes': {
        'task': 'security.tasks.migrate_user_emails_to_hash',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM (if needed)
    },
    
    # Cleanup Tasks (Weekly)
    'weekly-cleanup': {
        'task': 'reputation.tasks.cleanup_old_votes',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),  # Sunday at 4 AM
    },
    'security-events-cleanup': {
        'task': 'security.tasks.cleanup_security_events',
        'schedule': crontab(hour=5, minute=0, day_of_week=0),  # Sunday at 5 AM
    },
    
    # System Monitoring Tasks
    'system-health-check': {
        'task': 'ano_backend.monitoring_tasks.system_health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'performance-metrics-report': {
        'task': 'ano_backend.monitoring_tasks.performance_metrics_report',
        'schedule': crontab(hour='*/2', minute=0),  # Every 2 hours
    },
    'circuit-breaker-status': {
        'task': 'ano_backend.monitoring_tasks.circuit_breaker_status_check',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    'cleanup-monitoring-data': {
        'task': 'ano_backend.monitoring_tasks.cleanup_monitoring_data',
        'schedule': crontab(hour=6, minute=0, day_of_week=0),  # Sunday at 6 AM
    },
}

# Task routing configuration
CELERY_TASK_ROUTES = {
    # High priority tasks (real-time updates and user-facing emails)
    'reputation.tasks.update_message_ranking_realtime': {'queue': 'high_priority'},
    'moderation.tasks.moderate_message_async': {'queue': 'high_priority'},
    'authentication.tasks.send_verification_email': {'queue': 'high_priority'},
    'authentication.tasks.send_password_reset_email': {'queue': 'high_priority'},
    
    # Medium priority tasks (user-facing operations)
    'reputation.tasks.calculate_user_reputation': {'queue': 'medium_priority'},
    'reputation.tasks.update_wilson_scores': {'queue': 'medium_priority'},
    'security.tasks.analyze_security_events': {'queue': 'medium_priority'},
    
    # Low priority tasks (maintenance and reports)
    'reputation.tasks.batch_tier_updates': {'queue': 'low_priority'},
    'reputation.tasks.cleanup_old_votes': {'queue': 'low_priority'},
    'moderation.tasks.cleanup_expired_shadowbans': {'queue': 'low_priority'},
    'security.tasks.cleanup_rate_limit_records': {'queue': 'low_priority'},
    'security.tasks.cleanup_security_events': {'queue': 'low_priority'},
    
    # Report generation (separate queue)
    'reputation.tasks.generate_reputation_report': {'queue': 'reports'},
    'moderation.tasks.generate_heat_report': {'queue': 'reports'},
    'security.tasks.generate_security_report': {'queue': 'reports'},
    
    # Monitoring tasks (separate queue)
    'ano_backend.monitoring_tasks.system_health_check': {'queue': 'monitoring'},
    'ano_backend.monitoring_tasks.performance_metrics_report': {'queue': 'monitoring'},
    'ano_backend.monitoring_tasks.circuit_breaker_status_check': {'queue': 'monitoring'},
    'ano_backend.monitoring_tasks.cleanup_monitoring_data': {'queue': 'monitoring'},
}

# Task execution settings
CELERY_TASK_ANNOTATIONS = {
    # Set time limits for tasks
    'reputation.tasks.calculate_user_reputation': {'time_limit': 300},  # 5 minutes
    'reputation.tasks.update_wilson_scores': {'time_limit': 600},  # 10 minutes
    'reputation.tasks.batch_tier_updates': {'time_limit': 1800},  # 30 minutes
    'moderation.tasks.moderate_message_async': {'time_limit': 120},  # 2 minutes
    'moderation.tasks.update_user_heat_scores': {'time_limit': 900},  # 15 minutes
    'security.tasks.migrate_user_emails_to_hash': {'time_limit': 1800},  # 30 minutes
    'security.tasks.analyze_security_events': {'time_limit': 600},  # 10 minutes
    'ano_backend.monitoring_tasks.system_health_check': {'time_limit': 60},  # 1 minute
    'ano_backend.monitoring_tasks.performance_metrics_report': {'time_limit': 120},  # 2 minutes
    
    # Set rate limits for resource-intensive tasks
    'reputation.tasks.batch_tier_updates': {'rate_limit': '1/m'},  # 1 per minute
    'security.tasks.migrate_user_emails_to_hash': {'rate_limit': '1/m'},  # 1 per minute
    'moderation.tasks.batch_moderate_messages': {'rate_limit': '10/m'},  # 10 per minute
}

# Queue configuration
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'high_priority': {
        'exchange': 'high_priority',
        'exchange_type': 'direct',
        'routing_key': 'high_priority',
    },
    'medium_priority': {
        'exchange': 'medium_priority',
        'exchange_type': 'direct',
        'routing_key': 'medium_priority',
    },
    'low_priority': {
        'exchange': 'low_priority',
        'exchange_type': 'direct',
        'routing_key': 'low_priority',
    },
    'reports': {
        'exchange': 'reports',
        'exchange_type': 'direct',
        'routing_key': 'reports',
    },
    'monitoring': {
        'exchange': 'monitoring',
        'exchange_type': 'direct',
        'routing_key': 'monitoring',
    },
}

# Error handling configuration
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Monitoring and logging
CELERY_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# Result backend settings
CELERY_RESULT_EXPIRES = 3600  # 1 hour
CELERY_TASK_IGNORE_RESULT = False

# Worker settings
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 200000  # 200MB