#!/usr/bin/env python
"""
Test script for password reset functionality.
Tests both Celery task execution and direct email sending.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings
from authentication.tasks import send_password_reset_email
from django.core.mail import send_mail

User = get_user_model()

def test_direct_email():
    """Test direct email sending (bypass Celery)"""
    print("\n" + "="*60)
    print("TEST 1: Direct Email Sending (No Celery)")
    print("="*60)
    
    try:
        send_mail(
            subject='Test Password Reset Email',
            message='This is a test email to verify email functionality.',
            from_email=settings.EMAIL_HOST_USER or 'noreply@ano.com',
            recipient_list=['test@iiti.ac.in'],
            fail_silently=False,
        )
        print("✓ Direct email sent successfully!")
        print("  Check your terminal/console for the email output")
    except Exception as e:
        print(f"✗ Direct email failed: {str(e)}")
    
    print()

def test_celery_task_sync():
    """Test Celery task execution synchronously"""
    print("\n" + "="*60)
    print("TEST 2: Celery Task (Synchronous Execution)")
    print("="*60)
    
    # Get a test user
    email = input("Enter user email to test (or press Enter for first user): ").strip()
    
    try:
        if email:
            user = User.objects.get(email=email)
        else:
            user = User.objects.filter(is_active=True).first()
            if not user:
                print("✗ No active users found in database")
                return
        
        print(f"Testing with user: {user.email}")
        
        # Generate reset token
        reset_token = user.generate_password_reset_token()
        print(f"Generated reset token: {reset_token}")
        
        # Call task synchronously (without .delay())
        print("\nCalling Celery task synchronously...")
        result = send_password_reset_email(
            user_id=str(user.id),
            user_email=user.email,
            reset_token=str(reset_token)
        )
        
        print(f"✓ Task executed successfully: {result}")
        print("  Check your terminal/console for the email output")
        
        # Print reset URL
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={reset_token}"
        print(f"\nReset URL: {reset_url}")
        
    except User.DoesNotExist:
        print(f"✗ User not found: {email}")
    except Exception as e:
        print(f"✗ Task execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()

def test_celery_task_async():
    """Test Celery task execution asynchronously (requires Celery worker)"""
    print("\n" + "="*60)
    print("TEST 3: Celery Task (Asynchronous - Requires Worker)")
    print("="*60)
    
    # Get a test user
    email = input("Enter user email to test (or press Enter for first user): ").strip()
    
    try:
        if email:
            user = User.objects.get(email=email)
        else:
            user = User.objects.filter(is_active=True).first()
            if not user:
                print("✗ No active users found in database")
                return
        
        print(f"Testing with user: {user.email}")
        
        # Generate reset token
        reset_token = user.generate_password_reset_token()
        print(f"Generated reset token: {reset_token}")
        
        # Call task asynchronously (with .delay())
        print("\nQueuing Celery task asynchronously...")
        task = send_password_reset_email.delay(
            user_id=str(user.id),
            user_email=user.email,
            reset_token=str(reset_token)
        )
        
        print(f"✓ Task queued successfully!")
        print(f"  Task ID: {task.id}")
        print(f"  Task State: {task.state}")
        print("\n  Check your Celery worker terminal for task execution")
        print("  The email should appear in the Celery worker console")
        
        # Print reset URL
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={reset_token}"
        print(f"\nReset URL: {reset_url}")
        
    except User.DoesNotExist:
        print(f"✗ User not found: {email}")
    except Exception as e:
        print(f"✗ Task queueing failed: {str(e)}")
        print("\n  This usually means:")
        print("  1. Redis is not running")
        print("  2. Celery worker is not running")
        print("  3. Celery configuration is incorrect")
        import traceback
        traceback.print_exc()
    
    print()

def check_celery_connection():
    """Check if Celery can connect to Redis"""
    print("\n" + "="*60)
    print("CELERY CONNECTION CHECK")
    print("="*60)
    
    try:
        from ano_backend.celery import app
        
        # Try to ping Redis
        print("Checking Redis connection...")
        inspect = app.control.inspect()
        
        # Check active workers
        active = inspect.active()
        if active:
            print(f"✓ Celery workers found: {list(active.keys())}")
            for worker, tasks in active.items():
                print(f"  - {worker}: {len(tasks)} active tasks")
        else:
            print("✗ No active Celery workers found")
            print("\n  To start a Celery worker, run:")
            print("  cd backend")
            print("  celery -A ano_backend worker --loglevel=info")
        
        # Check registered tasks
        registered = inspect.registered()
        if registered:
            print(f"\n✓ Registered tasks found:")
            for worker, tasks in registered.items():
                auth_tasks = [t for t in tasks if 'authentication' in t]
                if auth_tasks:
                    print(f"  Authentication tasks on {worker}:")
                    for task in auth_tasks:
                        print(f"    - {task}")
        
    except Exception as e:
        print(f"✗ Celery connection failed: {str(e)}")
        print("\n  Make sure Redis is running:")
        print("  docker ps | grep redis")
    
    print()

def main():
    print("\n" + "="*60)
    print("PASSWORD RESET TESTING SCRIPT")
    print("="*60)
    print("\nThis script will test password reset functionality")
    print("in different ways to diagnose the issue.\n")
    
    # Check Celery connection first
    check_celery_connection()
    
    # Run tests
    test_direct_email()
    
    input("Press Enter to continue to synchronous task test...")
    test_celery_task_sync()
    
    input("Press Enter to continue to asynchronous task test...")
    test_celery_task_async()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nSUMMARY:")
    print("- If TEST 1 worked: Email backend is configured correctly")
    print("- If TEST 2 worked: Celery task code is correct")
    print("- If TEST 3 failed: Celery worker is not running or not connected")
    print("\nSOLUTION:")
    print("If Celery worker is not running, start it with:")
    print("  cd backend")
    print("  celery -A ano_backend worker --loglevel=info")
    print()

if __name__ == '__main__':
    main()
