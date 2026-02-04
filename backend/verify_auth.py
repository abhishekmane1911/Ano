#!/usr/bin/env python
"""Quick verification script for authentication implementation"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from authentication.models import User, validate_iiti_email
from django.core.exceptions import ValidationError

print("=" * 50)
print("Authentication Implementation Verification")
print("=" * 50)

# Test 1: Email validation
print("\n1. Testing email domain validation...")
try:
    validate_iiti_email('test@iiti.ac.in')
    print("   ✓ Valid @iiti.ac.in email accepted")
except ValidationError:
    print("   ✗ Valid email rejected (FAIL)")

try:
    validate_iiti_email('test@gmail.com')
    print("   ✗ Invalid email accepted (FAIL)")
except ValidationError:
    print("   ✓ Invalid email rejected")

# Test 2: User model
print("\n2. Testing User model...")
try:
    # Clean up any existing test user
    User.objects.filter(email='verify@iiti.ac.in').delete()
    
    user = User.objects.create_user(
        email='verify@iiti.ac.in',
        username='verifyuser',
        password='testpass123'
    )
    print(f"   ✓ User created with UUID: {user.id}")
    print(f"   ✓ Verification token: {user.verification_token}")
    print(f"   ✓ Password hashed: {user.password[:20]}...")
    print(f"   ✓ Is verified: {user.is_verified}")
    
    # Check password hashing
    if user.password.startswith('argon2'):
        print("   ✓ Argon2 password hashing confirmed")
    else:
        print("   ✗ Argon2 not used (FAIL)")
    
    # Clean up
    user.delete()
    
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check settings
print("\n3. Checking Django settings...")
from django.conf import settings

if settings.AUTH_USER_MODEL == 'authentication.User':
    print("   ✓ Custom User model configured")
else:
    print("   ✗ Custom User model not configured")

if 'authentication.middleware.RateLimitMiddleware' in settings.MIDDLEWARE:
    print("   ✓ Rate limiting middleware configured")
else:
    print("   ✗ Rate limiting middleware not configured")

if settings.PASSWORD_HASHERS[0] == 'django.contrib.auth.hashers.Argon2PasswordHasher':
    print("   ✓ Argon2 is primary password hasher")
else:
    print("   ✗ Argon2 not primary hasher")

# Test 4: Check endpoints
print("\n4. Checking URL configuration...")
from django.urls import reverse
try:
    reverse('authentication:register')
    print("   ✓ Registration endpoint configured")
    reverse('authentication:login')
    print("   ✓ Login endpoint configured")
    reverse('authentication:verify-email')
    print("   ✓ Email verification endpoint configured")
    reverse('authentication:refresh')
    print("   ✓ Token refresh endpoint configured")
    reverse('authentication:logout')
    print("   ✓ Logout endpoint configured")
    reverse('authentication:me')
    print("   ✓ User details endpoint configured")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 50)
print("Verification Complete!")
print("=" * 50)
