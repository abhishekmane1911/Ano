# Anonymous Logging - Quick Reference

## Import Loggers

```python
import logging
from ano_backend.logging_config import get_anonymous_id_from_user

# Get loggers
logger = logging.getLogger('ano_platform')
security_logger = logging.getLogger('ano_platform.security')
```

## Get Anonymous ID

```python
# In a view with request object
anonymous_id = get_anonymous_id_from_user(request.user)
```

## Log Patterns

### User Actions
```python
# Registration
logger.info(f"New user registered: user_{user.id}")

# Login
anonymous_id = get_anonymous_id_from_user(user)
logger.info(f"Successful login for {anonymous_id}")

# Logout
logger.info(f"User logged out: {anonymous_id}")
```

### Security Events
```python
# Failed login
security_logger.warning(f"Failed login attempt for email domain: {email.split('@')[1]}")

# Report created
security_logger.warning(
    f"Report created - Reporter: {reporter_id}, "
    f"Reported: {reported_id}, Reason: {reason}"
)

# User blocked
security_logger.warning(
    f"User blocked - Blocker: {blocker_id}, Blocked: {blocked_id}"
)

# User banned
security_logger.error(
    f"User banned by admin {admin_id} - "
    f"Banned user: {banned_id}, Reason: {reason}"
)
```

### Errors
```python
# General error
logger.error(f"Operation failed for {anonymous_id}: {error_message}")

# Exception with traceback
logger.exception(f"Exception occurred for {anonymous_id}")
```

## Log Levels

- **INFO**: Normal operations (login, logout, profile updates)
- **WARNING**: Potential issues (failed validations, security events)
- **ERROR**: Application errors (failed operations)
- **CRITICAL**: Critical security events (rarely used)

## View Logs

```bash
# Tail general logs
tail -f backend/logs/ano_platform.log

# Tail security logs
tail -f backend/logs/security.log

# Tail error logs
tail -f backend/logs/errors.log

# Search for specific anonymous ID
grep "a4b92671-5f02-4b00-bdc6-c6acd7f63569" backend/logs/ano_platform.log
```

## What NOT to Log

❌ Email addresses (automatically redacted)
❌ Real names (automatically redacted)
❌ Passwords
❌ JWT tokens
❌ Session IDs
❌ Any PII

## What TO Log

✅ Anonymous UUIDs
✅ User actions
✅ Operation results
✅ Error messages
✅ Security events

## Testing

```bash
# Run logging tests
python backend/test_logging.py
```

## Remember

1. Always use `get_anonymous_id_from_user()` for user identification
2. Use `security_logger` for security-related events
3. Include context (IDs, operation type, result)
4. Emails are automatically redacted by the formatter
5. Logs are automatically rotated (10MB, 10 backups)
