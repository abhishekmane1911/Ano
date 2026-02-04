"""
Custom logging configuration for Ano platform.
Ensures all logs use anonymous identifiers instead of emails or real names.
"""
import logging
import re
from typing import Optional


class AnonymousFormatter(logging.Formatter):
    """
    Custom formatter that replaces emails and sensitive information with anonymous identifiers.
    Ensures no PII (Personally Identifiable Information) appears in logs.
    """
    
    # Pattern to match email addresses
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    # Pattern to match common name patterns (first name, last name)
    # This is a basic pattern - adjust based on your needs
    NAME_PATTERN = re.compile(r'\b(first_name|last_name|full_name|name)[\s:=]+["\']?([^"\'}\s,]+)["\']?', re.IGNORECASE)
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record, replacing sensitive information with anonymous identifiers.
        """
        # Format the message first
        original_msg = super().format(record)
        
        # Replace email addresses with [EMAIL_REDACTED]
        sanitized_msg = self.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', original_msg)
        
        # Replace name fields with [NAME_REDACTED]
        sanitized_msg = self.NAME_PATTERN.sub(r'\1: [NAME_REDACTED]', sanitized_msg)
        
        return sanitized_msg


def get_anonymous_id_from_user(user) -> Optional[str]:
    """
    Extract anonymous_id from a user object.
    Returns the profile's anonymous_id if available, otherwise returns a generic identifier.
    
    Args:
        user: Django User object
        
    Returns:
        Anonymous identifier string or None
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        # Try to get the profile's anonymous_id
        if hasattr(user, 'profile') and user.profile:
            return str(user.profile.anonymous_id)
    except Exception:
        # Profile might not exist yet
        pass
    
    # Fallback to user UUID (still anonymous, not email)
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
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{log_dir}/errors.log',
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'security_file': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{log_dir}/security.log',
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 20,  # Keep more security logs
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
