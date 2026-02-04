"""
Manual tests for security middleware and protections.
Run with: python manage.py shell < test_security.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.test import RequestFactory, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from ano_backend.validators import (
    validate_email,
    validate_iiti_email,
    validate_password,
    validate_uuid,
    validate_age,
    validate_text_length,
    validate_choice,
    sanitize_html,
)
from ano_backend.file_validators import (
    validate_file_extension,
    validate_file_size,
    validate_image_file,
)
from ano_backend.middleware import SecurityHeadersMiddleware, HTTPSRedirectMiddleware


def test_email_validation():
    """Test email validation"""
    print("\n=== Testing Email Validation ===")
    
    # Valid emails
    try:
        validate_email("test@example.com")
        print("✓ Valid email accepted")
    except ValueError as e:
        print(f"✗ Valid email rejected: {e}")
    
    # Invalid emails
    try:
        validate_email("invalid-email")
        print("✗ Invalid email accepted")
    except ValueError:
        print("✓ Invalid email rejected")
    
    # IIT Indore email
    try:
        validate_iiti_email("student@iiti.ac.in")
        print("✓ Valid IITI email accepted")
    except ValueError as e:
        print(f"✗ Valid IITI email rejected: {e}")
    
    try:
        validate_iiti_email("student@gmail.com")
        print("✗ Non-IITI email accepted")
    except ValueError:
        print("✓ Non-IITI email rejected")


def test_password_validation():
    """Test password validation"""
    print("\n=== Testing Password Validation ===")
    
    # Valid password
    try:
        validate_password("SecurePass123")
        print("✓ Valid password accepted")
    except ValueError as e:
        print(f"✗ Valid password rejected: {e}")
    
    # Too short
    try:
        validate_password("short1")
        print("✗ Short password accepted")
    except ValueError:
        print("✓ Short password rejected")
    
    # No number
    try:
        validate_password("NoNumberPassword")
        print("✗ Password without number accepted")
    except ValueError:
        print("✓ Password without number rejected")
    
    # No letter
    try:
        validate_password("12345678")
        print("✗ Password without letter accepted")
    except ValueError:
        print("✓ Password without letter rejected")


def test_uuid_validation():
    """Test UUID validation"""
    print("\n=== Testing UUID Validation ===")
    
    # Valid UUID
    try:
        validate_uuid("550e8400-e29b-41d4-a716-446655440000")
        print("✓ Valid UUID accepted")
    except ValueError as e:
        print(f"✗ Valid UUID rejected: {e}")
    
    # Invalid UUID
    try:
        validate_uuid("not-a-uuid")
        print("✗ Invalid UUID accepted")
    except ValueError:
        print("✓ Invalid UUID rejected")


def test_age_validation():
    """Test age validation"""
    print("\n=== Testing Age Validation ===")
    
    # Valid age
    try:
        validate_age(25)
        print("✓ Valid age accepted")
    except ValueError as e:
        print(f"✗ Valid age rejected: {e}")
    
    # Too young
    try:
        validate_age(15)
        print("✗ Underage accepted")
    except ValueError:
        print("✓ Underage rejected")
    
    # Too old
    try:
        validate_age(150)
        print("✗ Age over 100 accepted")
    except ValueError:
        print("✓ Age over 100 rejected")


def test_html_sanitization():
    """Test HTML sanitization"""
    print("\n=== Testing HTML Sanitization ===")
    
    # Script tag
    dirty = "<script>alert('xss')</script>Hello"
    clean = sanitize_html(dirty)
    if "<script" not in clean.lower():
        print("✓ Script tag removed")
    else:
        print("✗ Script tag not removed")
    
    # Event handler
    dirty = '<div onclick="alert(\'xss\')">Click me</div>'
    clean = sanitize_html(dirty)
    if "onclick" not in clean.lower():
        print("✓ Event handler removed")
    else:
        print("✗ Event handler not removed")
    
    # JavaScript protocol
    dirty = '<a href="javascript:alert(\'xss\')">Link</a>'
    clean = sanitize_html(dirty)
    if "javascript:" not in clean.lower():
        print("✓ JavaScript protocol removed")
    else:
        print("✗ JavaScript protocol not removed")


def test_file_extension_validation():
    """Test file extension validation"""
    print("\n=== Testing File Extension Validation ===")
    
    # Valid extension
    try:
        validate_file_extension("image.jpg", ['.jpg', '.png'])
        print("✓ Valid extension accepted")
    except ValidationError as e:
        print(f"✗ Valid extension rejected: {e}")
    
    # Invalid extension
    try:
        validate_file_extension("malware.exe", ['.jpg', '.png'])
        print("✗ Invalid extension accepted")
    except ValidationError:
        print("✓ Invalid extension rejected")


def test_file_size_validation():
    """Test file size validation"""
    print("\n=== Testing File Size Validation ===")
    
    # Create a small file
    small_file = SimpleUploadedFile("test.jpg", b"x" * 1024, content_type="image/jpeg")
    
    try:
        validate_file_size(small_file, max_size=10 * 1024)  # 10 KB
        print("✓ Small file accepted")
    except ValidationError as e:
        print(f"✗ Small file rejected: {e}")
    
    # Create a large file
    large_file = SimpleUploadedFile("test.jpg", b"x" * (20 * 1024), content_type="image/jpeg")
    
    try:
        validate_file_size(large_file, max_size=10 * 1024)  # 10 KB
        print("✗ Large file accepted")
    except ValidationError:
        print("✓ Large file rejected")


def test_security_headers():
    """Test security headers middleware"""
    print("\n=== Testing Security Headers ===")
    
    factory = RequestFactory()
    request = factory.get('/')
    
    # Create a simple response
    def get_response(request):
        from django.http import HttpResponse
        return HttpResponse("OK")
    
    middleware = SecurityHeadersMiddleware(get_response)
    response = middleware(request)
    
    # Check for security headers
    headers_to_check = [
        'Content-Security-Policy',
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Referrer-Policy',
    ]
    
    for header in headers_to_check:
        if header in response:
            print(f"✓ {header} header present")
        else:
            print(f"✗ {header} header missing")


def test_choice_validation():
    """Test choice validation"""
    print("\n=== Testing Choice Validation ===")
    
    # Valid choice
    try:
        validate_choice('friendship', ['friendship', 'dating', 'casual'])
        print("✓ Valid choice accepted")
    except ValueError as e:
        print(f"✗ Valid choice rejected: {e}")
    
    # Invalid choice
    try:
        validate_choice('invalid', ['friendship', 'dating', 'casual'])
        print("✗ Invalid choice accepted")
    except ValueError:
        print("✓ Invalid choice rejected")


def test_text_length_validation():
    """Test text length validation"""
    print("\n=== Testing Text Length Validation ===")
    
    # Valid length
    try:
        validate_text_length("Hello World", min_length=5, max_length=20)
        print("✓ Valid length accepted")
    except ValueError as e:
        print(f"✗ Valid length rejected: {e}")
    
    # Too short
    try:
        validate_text_length("Hi", min_length=5, max_length=20)
        print("✗ Too short text accepted")
    except ValueError:
        print("✓ Too short text rejected")
    
    # Too long
    try:
        validate_text_length("x" * 100, min_length=5, max_length=20)
        print("✗ Too long text accepted")
    except ValueError:
        print("✓ Too long text rejected")


if __name__ == '__main__':
    print("=" * 60)
    print("SECURITY MIDDLEWARE AND PROTECTIONS TEST SUITE")
    print("=" * 60)
    
    test_email_validation()
    test_password_validation()
    test_uuid_validation()
    test_age_validation()
    test_html_sanitization()
    test_file_extension_validation()
    test_file_size_validation()
    test_security_headers()
    test_choice_validation()
    test_text_length_validation()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
