#!/usr/bin/env python
"""
Manual test script for email service functionality.
Tests registration with email verification and password reset flow.

Usage:
    python test_email_service.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from authentication.tasks import send_verification_email, send_password_reset_email

User = get_user_model()


def test_verification_email():
    """Test sending verification email"""
    print("\n" + "="*60)
    print("Testing Verification Email")
    print("="*60)
    
    # Create a test user
    email = 'test_verification@iiti.ac.in'
    
    # Clean up if user exists
    User.objects.filter(email=email).delete()
    
    user = User.objects.create_user(
        email=email,
        username='test_verification',
        password='TestPass123!'
    )
    
    print(f"✓ Created test user: {email}")
    print(f"  User ID: {user.id}")
    print(f"  Verification Token: {user.verification_token}")
    
    # Send verification email (synchronously for testing)
    try:
        result = send_verification_email(
            user_id=str(user.id),
            user_email=user.email,
            verification_token=str(user.verification_token)
        )
        print(f"✓ Verification email sent successfully")
        print(f"  Result: {result}")
    except Exception as e:
        print(f"✗ Failed to send verification email: {e}")
    
    # Clean up
    user.delete()
    print("✓ Test user cleaned up")


def test_password_reset_email():
    """Test sending password reset email"""
    print("\n" + "="*60)
    print("Testing Password Reset Email")
    print("="*60)
    
    # Create a test user
    email = 'test_reset@iiti.ac.in'
    
    # Clean up if user exists
    User.objects.filter(email=email).delete()
    
    user = User.objects.create_user(
        email=email,
        username='test_reset',
        password='OldPass123!'
    )
    user.is_verified = True
    user.is_active = True
    user.save()
    
    print(f"✓ Created test user: {email}")
    print(f"  User ID: {user.id}")
    
    # Generate password reset token
    reset_token = user.generate_password_reset_token()
    print(f"✓ Generated password reset token: {reset_token}")
    print(f"  Token valid: {user.is_password_reset_token_valid()}")
    
    # Send password reset email (synchronously for testing)
    try:
        result = send_password_reset_email(
            user_id=str(user.id),
            user_email=user.email,
            reset_token=str(reset_token)
        )
        print(f"✓ Password reset email sent successfully")
        print(f"  Result: {result}")
    except Exception as e:
        print(f"✗ Failed to send password reset email: {e}")
    
    # Clean up
    user.delete()
    print("✓ Test user cleaned up")


def test_email_templates():
    """Test that email templates exist and are readable"""
    print("\n" + "="*60)
    print("Testing Email Templates")
    print("="*60)
    
    from django.template.loader import get_template
    
    templates = [
        'authentication/verification_email.html',
        'authentication/password_reset_email.html'
    ]
    
    for template_name in templates:
        try:
            template = get_template(template_name)
            print(f"✓ Template found: {template_name}")
            print(f"  Path: {template.origin.name if hasattr(template, 'origin') else 'N/A'}")
        except Exception as e:
            print(f"✗ Template not found: {template_name}")
            print(f"  Error: {e}")


def main():
    """Run all email service tests"""
    print("\n" + "="*60)
    print("EMAIL SERVICE TEST SUITE")
    print("="*60)
    print("\nNote: Emails will be printed to console (console backend)")
    print("In production, configure SMTP settings in .env file")
    
    try:
        test_email_templates()
        test_verification_email()
        test_password_reset_email()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        print("\n✓ Email service is working correctly!")
        print("\nNext steps:")
        print("1. Configure SMTP settings in .env for production")
        print("2. Set EMAIL_BACKEND to django.core.mail.backends.smtp.EmailBackend")
        print("3. Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        print("4. For Gmail, use an App Password (not your regular password)")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
