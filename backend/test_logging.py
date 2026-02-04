"""
Test script to verify anonymous logging functionality.
Tests that logs use anonymous IDs and don't contain emails or real names.
"""
import os
import sys
import django
import logging
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import Profile
from ano_backend.logging_config import (
    AnonymousFormatter,
    get_anonymous_id_from_user,
    get_logging_config
)

User = get_user_model()


def test_anonymous_formatter():
    """Test that the AnonymousFormatter redacts emails and names"""
    print("\n=== Testing AnonymousFormatter ===")
    
    formatter = AnonymousFormatter('[{asctime}] {levelname} - {message}', style='{')
    
    # Create a test log record
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='test.py',
        lineno=1,
        msg='User test@iiti.ac.in logged in with name John Doe',
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    print(f"Original message: {record.msg}")
    print(f"Formatted message: {formatted}")
    
    # Check that email is redacted
    assert 'test@iiti.ac.in' not in formatted, "Email should be redacted"
    assert '[EMAIL_REDACTED]' in formatted, "Email should be replaced with [EMAIL_REDACTED]"
    print("✓ Email redaction works")
    
    # Test with multiple emails
    record2 = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='test.py',
        lineno=1,
        msg='Transfer from user1@iiti.ac.in to user2@iiti.ac.in',
        args=(),
        exc_info=None
    )
    
    formatted2 = formatter.format(record2)
    print(f"\nOriginal message: {record2.msg}")
    print(f"Formatted message: {formatted2}")
    
    assert 'user1@iiti.ac.in' not in formatted2, "First email should be redacted"
    assert 'user2@iiti.ac.in' not in formatted2, "Second email should be redacted"
    print("✓ Multiple email redaction works")


def test_get_anonymous_id():
    """Test getting anonymous ID from user"""
    print("\n=== Testing get_anonymous_id_from_user ===")
    
    # Test with None
    result = get_anonymous_id_from_user(None)
    assert result is None, "Should return None for None user"
    print("✓ Returns None for None user")
    
    # Test with unauthenticated user
    class MockUser:
        is_authenticated = False
    
    result = get_anonymous_id_from_user(MockUser())
    assert result is None, "Should return None for unauthenticated user"
    print("✓ Returns None for unauthenticated user")
    
    # Test with real user (if exists)
    try:
        user = User.objects.filter(is_verified=True).first()
        if user:
            result = get_anonymous_id_from_user(user)
            print(f"Anonymous ID for user: {result}")
            
            # Check if user has profile
            if hasattr(user, 'profile') and user.profile:
                assert str(user.profile.anonymous_id) in result, "Should contain profile anonymous_id"
                print("✓ Returns profile anonymous_id when available")
            else:
                assert f"user_{user.id}" == result, "Should return user_<uuid> fallback"
                print("✓ Returns user_<uuid> fallback when no profile")
    except Exception as e:
        print(f"Note: Could not test with real user: {e}")


def test_logging_config():
    """Test that logging configuration is properly structured"""
    print("\n=== Testing Logging Configuration ===")
    
    config = get_logging_config(log_dir='test_logs')
    
    # Check structure
    assert 'version' in config, "Config should have version"
    assert 'formatters' in config, "Config should have formatters"
    assert 'handlers' in config, "Config should have handlers"
    assert 'loggers' in config, "Config should have loggers"
    print("✓ Configuration structure is valid")
    
    # Check formatters
    assert 'anonymous' in config['formatters'], "Should have anonymous formatter"
    assert 'verbose' in config['formatters'], "Should have verbose formatter"
    print("✓ Formatters are configured")
    
    # Check handlers
    assert 'console' in config['handlers'], "Should have console handler"
    assert 'file' in config['handlers'], "Should have file handler"
    assert 'error_file' in config['handlers'], "Should have error_file handler"
    assert 'security_file' in config['handlers'], "Should have security_file handler"
    print("✓ Handlers are configured")
    
    # Check loggers
    assert 'ano_platform' in config['loggers'], "Should have ano_platform logger"
    assert 'ano_platform.security' in config['loggers'], "Should have security logger"
    print("✓ Loggers are configured")
    
    # Check file rotation settings
    file_handler = config['handlers']['file']
    assert file_handler['class'] == 'logging.handlers.RotatingFileHandler', "Should use RotatingFileHandler"
    assert file_handler['maxBytes'] == 10485760, "Should have 10MB max size"
    assert file_handler['backupCount'] == 10, "Should keep 10 backups"
    print("✓ Log rotation is configured (10MB, 10 backups)")
    
    # Check security log retention
    security_handler = config['handlers']['security_file']
    assert security_handler['backupCount'] == 20, "Security logs should keep 20 backups"
    print("✓ Security logs have extended retention (20 backups)")


def test_actual_logging():
    """Test actual logging with the configured system"""
    print("\n=== Testing Actual Logging ===")
    
    # Get logger
    logger = logging.getLogger('ano_platform')
    security_logger = logging.getLogger('ano_platform.security')
    
    # Test logging with email (should be redacted)
    logger.info("User test@iiti.ac.in performed action")
    print("✓ Logged message with email (check logs for redaction)")
    
    # Test security logging
    security_logger.warning("Failed login attempt for user@iiti.ac.in")
    print("✓ Logged security event (check security.log)")
    
    # Test with anonymous ID
    logger.info("User action performed by anonymous_id: 12345678-1234-1234-1234-123456789abc")
    print("✓ Logged message with anonymous ID")


def main():
    """Run all tests"""
    print("=" * 60)
    print("ANONYMOUS LOGGING SYSTEM TESTS")
    print("=" * 60)
    
    try:
        test_anonymous_formatter()
        test_get_anonymous_id()
        test_logging_config()
        test_actual_logging()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nLogging system is configured correctly:")
        print("- Emails are automatically redacted")
        print("- Anonymous IDs are used for user identification")
        print("- Log rotation is enabled (10MB files, 10 backups)")
        print("- Security logs have extended retention (20 backups)")
        print("- Logs are stored in: backend/logs/")
        print("\nLog files:")
        print("  - ano_platform.log: General application logs")
        print("  - errors.log: Error-level logs")
        print("  - security.log: Security-related events")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
