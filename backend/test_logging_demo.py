"""
Demo script showing the anonymous logging system in action.
Simulates various operations and shows how logs are created.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

import logging
from django.contrib.auth import get_user_model
from ano_backend.logging_config import get_anonymous_id_from_user

User = get_user_model()

# Get loggers
logger = logging.getLogger('ano_platform')
security_logger = logging.getLogger('ano_platform.security')


def demo_authentication_logging():
    """Demonstrate authentication logging"""
    print("\n" + "="*60)
    print("DEMO: Authentication Logging")
    print("="*60)
    
    # Simulate registration
    logger.info("New user registered: user_12345678-1234-1234-1234-123456789abc")
    print("✓ Logged registration with user UUID")
    
    # Simulate email verification
    logger.info("Email verified successfully for user_12345678-1234-1234-1234-123456789abc")
    print("✓ Logged email verification")
    
    # Simulate successful login
    logger.info("Successful login for a4b92671-5f02-4b00-bdc6-c6acd7f63569")
    print("✓ Logged successful login with anonymous ID")
    
    # Simulate failed login (note: email is automatically redacted)
    security_logger.warning("Failed login attempt for user@iiti.ac.in")
    print("✓ Logged failed login (email will be redacted)")
    
    # Simulate logout
    logger.info("User logged out: a4b92671-5f02-4b00-bdc6-c6acd7f63569")
    print("✓ Logged logout")


def demo_safety_logging():
    """Demonstrate safety and moderation logging"""
    print("\n" + "="*60)
    print("DEMO: Safety & Moderation Logging")
    print("="*60)
    
    # Simulate report creation
    security_logger.warning(
        "Report created - Reporter: abc12345-1234-1234-1234-123456789abc, "
        "Reported: def67890-1234-1234-1234-123456789abc, "
        "Reason: harassment"
    )
    print("✓ Logged report creation with anonymous IDs")
    
    # Simulate report escalation
    security_logger.error(
        "Report escalation triggered for def67890-1234-1234-1234-123456789abc "
        "with 3 pending reports"
    )
    print("✓ Logged report escalation")
    
    # Simulate user block
    security_logger.warning(
        "User blocked - Blocker: abc12345-1234-1234-1234-123456789abc, "
        "Blocked: xyz99999-1234-1234-1234-123456789abc"
    )
    print("✓ Logged user block")
    
    # Simulate admin action
    security_logger.error(
        "User banned by admin admin123-1234-1234-1234-123456789abc - "
        "Banned user: bad12345-1234-1234-1234-123456789abc, "
        "Reason: Multiple policy violations"
    )
    print("✓ Logged admin ban action")


def demo_pii_redaction():
    """Demonstrate automatic PII redaction"""
    print("\n" + "="*60)
    print("DEMO: Automatic PII Redaction")
    print("="*60)
    
    # These messages contain PII that will be automatically redacted
    logger.info("User john.doe@iiti.ac.in updated their profile")
    print("✓ Email in log message (will be redacted)")
    
    logger.info("Profile update for user with name: John Doe")
    print("✓ Name in log message (will be redacted)")
    
    logger.info("Transfer from alice@iiti.ac.in to bob@iiti.ac.in completed")
    print("✓ Multiple emails in log message (will be redacted)")
    
    # This is the correct way - using anonymous IDs
    logger.info("Profile updated for user: a4b92671-5f02-4b00-bdc6-c6acd7f63569")
    print("✓ Correct: Using anonymous ID (no redaction needed)")


def demo_request_logging():
    """Demonstrate request logging"""
    print("\n" + "="*60)
    print("DEMO: HTTP Request Logging")
    print("="*60)
    
    # Simulate request logs (these would normally come from middleware)
    logger.info(
        "GET /api/profiles/me/ - Status: 200 - Duration: 0.045s - "
        "User: a4b92671-5f02-4b00-bdc6-c6acd7f63569"
    )
    print("✓ Logged GET request with anonymous ID")
    
    logger.warning(
        "POST /api/auth/login/ - Status: 401 - Duration: 0.123s - "
        "User: anonymous - IP: 192.168.1.100"
    )
    print("✓ Logged failed login attempt")
    
    logger.error(
        "POST /api/matchmaking/swipe/ - Status: 500 - Duration: 0.234s - "
        "User: a4b92671-5f02-4b00-bdc6-c6acd7f63569 - IP: 192.168.1.100"
    )
    print("✓ Logged server error")


def show_log_files():
    """Show the log files that were created"""
    print("\n" + "="*60)
    print("LOG FILES CREATED")
    print("="*60)
    
    logs_dir = Path(__file__).parent / 'logs'
    
    if logs_dir.exists():
        for log_file in sorted(logs_dir.glob('*.log')):
            size = log_file.stat().st_size
            print(f"\n{log_file.name} ({size} bytes)")
            print("-" * 60)
            
            # Show last 5 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-5:]:
                    print(line.rstrip())
    else:
        print("No log files found yet")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" "*15 + "ANONYMOUS LOGGING SYSTEM DEMO")
    print("="*70)
    print("\nThis demo shows how the logging system works in practice.")
    print("All logs use anonymous IDs and automatically redact PII.")
    print("="*70)
    
    demo_authentication_logging()
    demo_safety_logging()
    demo_pii_redaction()
    demo_request_logging()
    show_log_files()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Points:")
    print("1. All user references use anonymous UUIDs")
    print("2. Emails are automatically redacted to [EMAIL_REDACTED]")
    print("3. Names are automatically redacted to [NAME_REDACTED]")
    print("4. Security events go to separate security.log")
    print("5. Logs are automatically rotated at 10MB")
    print("\nCheck the log files in backend/logs/ to see the results!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
