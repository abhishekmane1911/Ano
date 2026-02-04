#!/usr/bin/env python
"""
Test script for password reset functionality
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from authentication.models import User

def test_password_reset():
    """Test password reset token generation and validation"""
    try:
        # Get user by email
        email = 'cse240001025@iiti.ac.in'
        user = User.objects.get(email=email)
        
        print(f"User found: {user.email}")
        print(f"User ID: {user.id}")
        print(f"Is active: {user.is_active}")
        print(f"Is verified: {user.is_verified}")
        
        # Check current reset token
        print(f"\nCurrent reset token: {user.password_reset_token}")
        print(f"Token created at: {user.password_reset_token_created}")
        
        if user.password_reset_token:
            print(f"Is token valid: {user.is_password_reset_token_valid()}")
            reset_url = f"http://localhost:5173/password-reset-confirm?token={user.password_reset_token}"
            print(f"\nReset URL: {reset_url}")
        else:
            print("No reset token found. Generating new one...")
            token = user.generate_password_reset_token()
            print(f"New token generated: {token}")
            reset_url = f"http://localhost:5173/password-reset-confirm?token={token}"
            print(f"Reset URL: {reset_url}")
            
    except User.DoesNotExist:
        print(f"User with email {email} not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_password_reset()