# Anonymous Logging Implementation

## Overview

The Ano platform implements a comprehensive logging system that ensures complete anonymity by automatically redacting personally identifiable information (PII) from all log entries. This system uses custom formatters, middleware, and logging configuration to maintain user privacy while providing detailed operational insights.

## Key Features

### 1. Automatic PII Redaction
- **Email Redaction**: All email addresses are automatically replaced with `[EMAIL_REDACTED]`
- **Name Redaction**: Name fields (first_name, last_name, full_name) are replaced with `[NAME_REDACTED]`
- **Anonymous Identifiers**: All user references use UUID-based anonymous identifiers

### 2. Log Rotation
- **File Size Limit**: 10 MB per log file
- **Backup Count**: 10 backup files for general logs
- **Security Logs**: 20 backup files for extended retention
- **Automatic Rotation**: Old logs are automatically archived when size limit is reached

### 3. Multiple Log Levels
- **INFO**: General application events (user actions, system operations)
- **WARNING**: Potential issues (failed validations, rate limiting)
- **ERROR**: Application errors (failed operations, exceptions)
- **CRITICAL**: Security events (failed logins, bans, reports)

## Architecture

### Components

#### 1. AnonymousFormatter (`ano_backend/logging_config.py`)
Custom logging formatter that sanitizes log messages:
```python
from ano_backend.logging_config import AnonymousFormatter

formatter = AnonymousFormatter('[{asctime}] {levelname} - {message}', style='{')
```

Features:
- Regex-based email detection and redaction
- Name field detection and redaction
- Preserves log structure and readability

#### 2. AnonymousLoggingMiddleware (`ano_backend/middleware.py`)
Django middleware that logs all HTTP requests:
```python
class AnonymousLoggingMiddleware:
    """Logs all requests using anonymous identifiers"""
```

Logs:
- Request method and path
- Response status code
- Request duration
- User's anonymous ID (if authenticated)
- Client IP address

#### 3. Logging Configuration (`ano_backend/settings.py`)
Django logging configuration with multiple handlers:
```python
from ano_backend.logging_config import get_logging_config
LOGGING = get_logging_config(log_dir=str(LOGS_DIR))
```

## Log Files

### Location
All logs are stored in: `backend/logs/`

### Files

#### 1. `ano_platform.log`
General application logs including:
- User registrations (with user_<uuid>)
- Login/logout events (with anonymous_id)
- Profile operations
- Message operations
- Match operations

#### 2. `errors.log`
Error-level logs including:
- Application exceptions
- Failed operations
- Database errors
- API errors

#### 3. `security.log`
Security-related events including:
- Failed login attempts
- Report submissions
- User blocks
- Admin moderation actions
- User bans
- Report escalations

## Usage

### In Views

```python
import logging
from ano_backend.logging_config import get_anonymous_id_from_user

# Get loggers
logger = logging.getLogger('ano_platform')
security_logger = logging.getLogger('ano_platform.security')

# Log with anonymous ID
def my_view(request):
    anonymous_id = get_anonymous_id_from_user(request.user)
    logger.info(f"Action performed by {anonymous_id}")
    
    # Security event
    security_logger.warning(f"Security event for {anonymous_id}")
```

### Critical Operations Logged

#### Authentication
- User registration: `user_<uuid>`
- Email verification: `user_<uuid>`
- Login success: `anonymous_id`
- Login failure: domain only (not full email)
- Logout: `anonymous_id`

#### Safety & Moderation
- Report creation: reporter and reported anonymous IDs
- Report escalation: reported user's anonymous ID
- User block: blocker and blocked anonymous IDs
- User unblock: blocker and unblocked anonymous IDs
- Admin report updates: admin ID, report ID, status change
- User ban: admin ID, banned user's anonymous ID, reason

#### Request Logging (Middleware)
- All HTTP requests with anonymous ID
- Response status codes
- Request duration
- Client IP (for rate limiting)

## Testing

Run the logging test suite:
```bash
python backend/test_logging.py
```

Tests verify:
- Email redaction works correctly
- Name redaction works correctly
- Anonymous ID extraction works
- Log rotation is configured
- Log files are created
- Formatters are applied

## Security Considerations

### What is Logged
✅ Anonymous UUIDs
✅ User actions and events
✅ System operations
✅ Error messages
✅ Request paths and methods
✅ Response status codes
✅ IP addresses (for security)

### What is NOT Logged
❌ Email addresses (redacted)
❌ Real names (redacted)
❌ Passwords
❌ JWT tokens
❌ Session IDs
❌ Personal information

## Configuration

### Environment Variables
No additional environment variables required. Logging is configured automatically.

### Customization

To adjust log levels or add new loggers, modify `ano_backend/logging_config.py`:

```python
def get_logging_config(log_dir: str = 'logs'):
    return {
        'loggers': {
            'my_custom_logger': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
```

### Log Rotation Settings

Adjust in `ano_backend/logging_config.py`:
```python
'file': {
    'maxBytes': 10485760,  # 10 MB
    'backupCount': 10,      # Keep 10 backups
}
```

## Monitoring

### View Recent Logs
```bash
# General logs
tail -f backend/logs/ano_platform.log

# Error logs
tail -f backend/logs/errors.log

# Security logs
tail -f backend/logs/security.log
```

### Search Logs
```bash
# Find all actions by a specific anonymous ID
grep "a4b92671-5f02-4b00-bdc6-c6acd7f63569" backend/logs/ano_platform.log

# Find all failed login attempts
grep "Failed login" backend/logs/security.log

# Find all report escalations
grep "escalation" backend/logs/security.log
```

## Compliance

This logging system ensures compliance with:
- **Requirement 14.3**: "WHEN the Ano System logs events, THEN the Ano System SHALL use anonymous identifiers in all log entries"
- **Property 19**: "For any logged event, the log entry should contain only anonymous identifiers, never institute emails or real names"

## Maintenance

### Log Cleanup
Logs are automatically rotated, but you can manually clean old logs:
```bash
# Remove logs older than 30 days
find backend/logs/ -name "*.log.*" -mtime +30 -delete
```

### Backup Logs
For long-term storage:
```bash
# Archive logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz backend/logs/

# Move to backup location
mv logs-backup-*.tar.gz /path/to/backup/
```

## Troubleshooting

### Logs Not Being Created
1. Check that `backend/logs/` directory exists
2. Verify write permissions: `ls -la backend/logs/`
3. Check Django settings: `LOGGING` configuration is loaded

### Emails Not Being Redacted
1. Verify `AnonymousFormatter` is being used
2. Check formatter configuration in `get_logging_config()`
3. Run test suite: `python backend/test_logging.py`

### Logs Too Large
1. Reduce `maxBytes` in logging configuration
2. Reduce `backupCount` to keep fewer backups
3. Implement log archival strategy

## Best Practices

1. **Always use anonymous IDs**: Use `get_anonymous_id_from_user()` helper
2. **Choose appropriate log level**: INFO for normal operations, WARNING for issues, ERROR for failures
3. **Use security logger for sensitive events**: Reports, blocks, bans, etc.
4. **Include context**: Add relevant IDs and operation details
5. **Don't log sensitive data**: Passwords, tokens, session IDs
6. **Monitor security logs regularly**: Check for suspicious patterns

## Example Log Entries

### Good Examples ✅
```
[2025-12-03 12:00:00] INFO ano_platform - User logged in: a4b92671-5f02-4b00-bdc6-c6acd7f63569
[2025-12-03 12:00:01] WARNING ano_platform.security - Report created - Reporter: abc123, Reported: def456, Reason: harassment
[2025-12-03 12:00:02] ERROR ano_platform.security - User banned by admin user_789 - Banned user: xyz999, Reason: Multiple violations
```

### Bad Examples ❌
```
# DON'T: Include email addresses
User logged in: john.doe@iiti.ac.in

# DON'T: Include real names
Profile updated for John Doe

# DON'T: Include passwords or tokens
Login failed for user@iiti.ac.in with password: secret123
```

## Summary

The anonymous logging system provides comprehensive operational visibility while maintaining complete user anonymity. All PII is automatically redacted, logs are rotated for efficient storage, and security events are tracked separately for enhanced monitoring.
