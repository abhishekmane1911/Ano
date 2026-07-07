import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ano_backend.settings")

app = Celery("ano_backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load advanced gamification module task configuration
try:
    from .celery_config import (
        CELERY_BEAT_SCHEDULE,
        CELERY_TASK_ROUTES,
        CELERY_TASK_ANNOTATIONS,
        CELERY_TASK_QUEUES,
        CELERY_TASK_DEFAULT_QUEUE,
        CELERY_TASK_REJECT_ON_WORKER_LOST,
        CELERY_TASK_ACKS_LATE,
        CELERY_WORKER_PREFETCH_MULTIPLIER,
        CELERY_SEND_TASK_EVENTS,
        CELERY_TASK_SEND_SENT_EVENT,
        CELERY_RESULT_EXPIRES,
        CELERY_TASK_IGNORE_RESULT,
        CELERY_WORKER_MAX_TASKS_PER_CHILD,
        CELERY_WORKER_MAX_MEMORY_PER_CHILD,
    )
    
    # Apply advanced configuration
    app.conf.beat_schedule = CELERY_BEAT_SCHEDULE
    app.conf.task_routes = CELERY_TASK_ROUTES
    app.conf.task_annotations = CELERY_TASK_ANNOTATIONS
    app.conf.task_queues = CELERY_TASK_QUEUES
    app.conf.task_default_queue = CELERY_TASK_DEFAULT_QUEUE
    app.conf.task_reject_on_worker_lost = CELERY_TASK_REJECT_ON_WORKER_LOST
    app.conf.task_acks_late = CELERY_TASK_ACKS_LATE
    app.conf.worker_prefetch_multiplier = CELERY_WORKER_PREFETCH_MULTIPLIER
    app.conf.task_send_sent_event = CELERY_TASK_SEND_SENT_EVENT
    app.conf.result_expires = CELERY_RESULT_EXPIRES
    app.conf.task_ignore_result = CELERY_TASK_IGNORE_RESULT
    app.conf.worker_max_tasks_per_child = CELERY_WORKER_MAX_TASKS_PER_CHILD
    app.conf.worker_max_memory_per_child = CELERY_WORKER_MAX_MEMORY_PER_CHILD
    
except ImportError:
    # Fallback to basic configuration if advanced config is not available
    pass

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Explicitly import monitoring_tasks since it doesn't follow the default 'tasks.py' naming convention
import ano_backend.monitoring_tasks


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
