# Security Implementation Guide

This document describes the security middleware and protections implemented in the Ano platform.

## Overview

The platform implements comprehensive security measures including:
- CORS configuration with allowed origins
- CSRF protection for all state-changing endpoints
- Input validation decorators for API endpoints
- Content Security Policy (CSP) headers
- File upload validation (type, size, content verification)
- HTTPS redirect middleware (production only)
- Secure cookie settings

## Security Middleware

### 1. HTTPSRedirectMiddleware

Automatically redirects all HTTP requests to HTTPS in production (when `DEBUG=False`).

**Location:** `ano_backend/middleware.py`

**Configuration:**
- Only active when `DEBUG=False`
- Returns 301 permanent redirect to HTTPS URL

### 2. SecurityHeadersMiddleware

Adds comprehensive security headers to all responses.

**Location:** `ano_backend/middleware.py`

**Headers Added:**
- `Content-Security-Policy`: Restricts resource loading sources
- `X-Content-Type-Options`: Prevents MIME type sniffing
- `X-Frame-Options`: Prevents clickjacking
- `X-XSS-Protection`: Enables browser XSS filter
- `Referrer-Policy`: Controls referrer information
- `Permissions-Policy`: Restricts browser features

### 3. RateLimitMiddleware

Prevents brute-force attacks on login endpoint.

**Location:** `authentication/middleware.py`

**Configuration:**
- Max attempts: 5 failed logins
- Lockout duration: 5 minutes
- Attempt window: 5 minutes

## CORS Configuration

CORS is configured to allow requests only from specified origins.

**Settings:**
```python
CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['accept', 'authorization', 'content-type', 'x-csrftoken', ...]
```

**Production:** Update `CORS_ALLOWED_ORIGINS` environment variable with production frontend URL.

## CSRF Protection

Django's built-in CSRF protection is enabled for all state-changing requests (POST, PUT, PATCH, DELETE).

**Settings:**
```python
CSRF_COOKIE_SECURE = True  # HTTPS only in production
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access
CSRF_COOKIE_SAMESITE = 'Lax'  # Additional protection
```

**Frontend Integration:**
The frontend must include the CSRF token in request headers:
```javascript
headers: {
  'X-CSRFToken': getCookie('csrftoken')
}
```

## Input Validation

### Validation Decorators

Use validation decorators to validate request data before processing.

**Location:** `ano_backend/validators.py`

**Example Usage:**
```python
from ano_backend.validators import validate_request_data, validate_email, validate_age

@validate_request_data(
    required_fields=['email', 'password', 'age'],
    optional_fields=['bio'],
    field_validators={
        'email': validate_email,
        'age': validate_age
    }
)
def my_view(request):
    # Request data is already validated
    data = request.data
    ...
```

### Available Validators

- `validate_email(email)`: Validates email format
- `validate_iiti_email(email)`: Validates IIT Indore email domain
- `validate_password(password)`: Validates password strength
- `validate_uuid(value)`: Validates UUID format
- `validate_age(age)`: Validates age range (18-100)
- `validate_text_length(text, min_length, max_length)`: Validates text length
- `validate_choice(value, choices)`: Validates value is in allowed choices
- `validate_json_array(value, item_validator, max_items)`: Validates JSON arrays
- `sanitize_html(text)`: Removes dangerous HTML/script tags

### Custom Validators

Create custom validators by raising `ValueError`:

```python
def validate_username(username):
    if not username.isalnum():
        raise ValueError('Username must be alphanumeric')
    if len(username) < 3:
        raise ValueError('Username must be at least 3 characters')
```

## File Upload Validation

Comprehensive validation for file uploads to prevent malicious files.

**Location:** `ano_backend/file_validators.py`

### Supported File Types

**Images:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- Max size: 10 MB
- Max dimensions: 4096x4096 px

**Audio:**
- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- WebM (.webm)
- Max size: 5 MB

### Usage in Views

```python
from ano_backend.file_validators import validate_uploaded_file
from django.core.exceptions import ValidationError

def upload_avatar(request):
    file = request.FILES.get('avatar')
    
    try:
        validate_uploaded_file(file, file_type='image')
    except ValidationError as e:
        return Response({
            'error': {
                'code': 'INVALID_FILE',
                'message': str(e)
            }
        }, status=400)
    
    # File is valid, proceed with upload
    ...
```

### Usage in Serializers

```python
from rest_framework import serializers
from ano_backend.file_validators import validate_uploaded_file

class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    
    def validate_avatar(self, value):
        if value:
            validate_uploaded_file(value, file_type='image')
        return value
```

### Validation Layers

1. **File Size**: Checks file size before processing
2. **Extension**: Validates file extension
3. **MIME Type**: Checks actual file content (not just extension)
4. **Content Verification**: Uses Pillow to verify image integrity
5. **Malware Scanning**: Basic pattern matching (placeholder for ClamAV integration)

## Secure Cookie Settings

Cookies are configured with security best practices.

**Settings:**
```python
SESSION_COOKIE_SECURE = True  # HTTPS only (production)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
CSRF_COOKIE_SECURE = True  # HTTPS only (production)
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access
CSRF_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

## HTTPS/SSL Settings (Production)

When `DEBUG=False`, the following settings are automatically enabled:

```python
SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Content Security Policy (CSP)

CSP headers restrict where resources can be loaded from.

**Default Policy:**
```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval';
style-src 'self' 'unsafe-inline';
img-src 'self' data: blob: https:;
font-src 'self' data:;
connect-src 'self' ws: wss:;
media-src 'self' blob:;
object-src 'none';
base-uri 'self';
form-action 'self';
frame-ancestors 'none';
```

**Note:** `unsafe-inline` and `unsafe-eval` are allowed for React development. In production, consider using nonces or hashes for stricter CSP.

## Environment Variables

Security-related environment variables:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# CSRF
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend URL (for email links)
FRONTEND_URL=https://yourdomain.com
```

## Testing Security Features

### Test CSRF Protection

```bash
# Should fail without CSRF token
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@iiti.ac.in","password":"test123"}'

# Should succeed with CSRF token
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{"email":"test@iiti.ac.in","password":"test123"}'
```

### Test Rate Limiting

```bash
# Make 6 failed login attempts rapidly
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"email":"test@iiti.ac.in","password":"wrong"}'
done
# 6th request should return 429 Too Many Requests
```

### Test File Upload Validation

```bash
# Try uploading invalid file type
curl -X POST http://localhost:8000/api/profiles/avatar/ \
  -H "Authorization: Bearer your-token" \
  -F "avatar=@malicious.exe"
# Should return 400 with validation error
```

## Security Checklist

- [x] CORS configured with allowed origins
- [x] CSRF protection enabled for state-changing endpoints
- [x] Input validation decorators available for all endpoints
- [x] Content Security Policy headers configured
- [x] File upload validation (type, size, content)
- [x] HTTPS redirect middleware (production)
- [x] Secure cookie settings (HttpOnly, Secure, SameSite)
- [x] Rate limiting on authentication endpoints
- [x] XSS protection headers
- [x] Clickjacking protection (X-Frame-Options)
- [x] MIME type sniffing prevention
- [x] HSTS headers (production)
- [x] Password hashing with Argon2
- [x] JWT token security (short-lived access tokens)

## Future Enhancements

1. **Malware Scanning**: Integrate ClamAV for comprehensive malware scanning
2. **WAF Integration**: Add Web Application Firewall for additional protection
3. **DDoS Protection**: Implement rate limiting at infrastructure level
4. **Security Monitoring**: Add logging and alerting for security events
5. **Penetration Testing**: Regular security audits and penetration testing
6. **Dependency Scanning**: Automated scanning for vulnerable dependencies

## References

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
