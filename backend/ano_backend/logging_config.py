import logging
import re
from typing import Optional


class AnonymousFormatter(logging.Formatter):
    
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    NAME_PATTERN = re.compile(r'\b(first_name|last_name|full_name|name)[\s:=]+["\']?([^"\'}\s,]+)["\']?', re.IGNORECASE)
    
    def format(self, record: logging.LogRecord) -> str:
        original_msg = super().format(record)
        
        sanitized_msg = self.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', original_msg)
        
        sanitized_msg = self.NAME_PATTERN.sub(r'\1: [NAME_REDACTED]', sanitized_msg)
        
        return sanitized_msg


def get_anonymous_id_from_user(user) -> Optional[str]:
    if not user or not user.is_authenticated:
        return None
    
    try:
        if hasattr(user, 'profile'):
            profile = getattr(user, 'profile', None)
            if profile and hasattr(profile, 'anonymous_id'):
                return str(profile.anonymous_id)
    except Exception as e:
        pass
    

    return f"user_{user.id}"


def get_logging_config(log_dir: str = 'logs'):
    """
    Generate Django logging configuration with anonymous formatting.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        Dictionary with Django logging configuration
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'anonymous': {
                '()': 'ano_backend.logging_config.AnonymousFormatter',
                'format': '[{asctime}] {levelname} {name} - {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'verbose': {
                '()': 'ano_backend.logging_config.AnonymousFormatter',
                'format': '[{asctime}] {levelname} [{name}:{lineno}] {funcName} - {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'anonymous',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{log_dir}/ano_platform.log',
                'maxBytes': 10485760, 
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{log_dir}/errors.log',
                'maxBytes': 10485760, 
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'security_file': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{log_dir}/security.log',
                'maxBytes': 10485760, 
                'backupCount': 20, 
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['error_file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.security': {
                'handlers': ['security_file'],
                'level': 'WARNING',
                'propagate': False,
            },
            'ano_platform': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'ano_platform.security': {
                'handlers': ['security_file', 'console'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    }
