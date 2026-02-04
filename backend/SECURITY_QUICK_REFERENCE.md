# Security Quick Reference Guide

Quick reference for developers implementing security features in the Ano platform.

## Input Validation

### Using Validation Decorators

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
@api_view(['POST'])
def my_view(request):
    # Data is already validated
    data = request.data
    # ... process data
```

### Available Validators

```python
from ano_backend.validators import (
    validate_email,           # Email format
    validate_iiti_email,      # IIT Indore email
    validate_password,        # Password strength
    validate_uuid,            # UUID format
    validate_age,             # Age range (18-100)
    validate_text_length,     # Text length
    validate_choice,          # Value in choices
    validate_json_array,      # JSON array
    sanitize_html,            # Remove dangerous HTML
)
```

### Custom Validators

```python
def validate_username(username):
    if not username.isalnum():
        raise ValueError('Username must be alphanumeric')
    if len(username) < 3:
        raise ValueError('Username must be at least 3 characters')
```

## File Upload Validation

### In Views

```python
from ano_backend.file_validators import validate_uploaded_file
from django.core.exceptions import ValidationError

@api_view(['POST'])
def upload_avatar(request):
    file = request.FILES.get('avatar')
    
    try:
        validate_uploaded_file(file, file_type='image')
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)
    
    # File is valid, proceed with upload
```

### In Serializers

```python
from rest_framework import serializers
from ano_backend.file_validators import validate_uploaded_file
from django.core.exceptions import ValidationError as DjangoValidationError

class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    
    def validate_avatar(self, value):
        if value:
            try:
                validate_uploaded_file(value, file_type='image')
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
```

## Security Headers

Headers are automatically added by `SecurityHeadersMiddleware`:

- Content-Security-Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: geolocation=(), microphone=(), camera=()

## CSRF Protection

### Frontend Integration

```javascript
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Include in requests
axios.post('/api/endpoint/', data, {
    headers: {
        'X-CSRFToken': getCookie('csrftoken')
    }
});
```

### Exempt Specific Views (Use Sparingly)

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def webhook_view(request):
    # Only for external webhooks
    pass
```

## Rate Limiting

Rate limiting is automatically applied to login endpoint by `RateLimitMiddleware`:

- Max attempts: 5 failed logins
- Lockout duration: 5 minutes
- Attempt window: 5 minutes

### Custom Rate Limiting

```python
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status

def rate_limit_check(request, key_prefix, max_attempts=10, window=60):
    """
    Check rate limit for a specific action.
    
    Args:
        request: Django request object
        key_prefix: Prefix for cache key (e.g., 'api_call')
        max_attempts: Maximum attempts allowed
        window: Time window in seconds
    
    Returns:
        True if rate limit exceeded, False otherwise
    """
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f'{key_prefix}_{ip}'
    
    attempts = cache.get(cache_key, 0)
    if attempts >= max_attempts:
        return True
    
    cache.set(cache_key, attempts + 1, window)
    return False

# Usage in view
@api_view(['POST'])
def my_view(request):
    if rate_limit_check(request, 'my_action', max_attempts=10, window=60):
        return Response(
            {'error': 'Rate limit exceeded'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    # ... process request
```

## Password Security

### Hashing (Automatic)

Django automatically hashes passwords using Argon2:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create_user(
    email='user@iiti.ac.in',
    password='SecurePass123'  # Automatically hashed
)
```

### Validation

```python
from ano_backend.validators import validate_password

try:
    validate_password('SecurePass123')
except ValueError as e:
    # Handle validation error
    pass
```

## JWT Tokens

### Token Generation (Automatic)

```python
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
```

### Token Validation (Automatic)

DRF automatically validates tokens when using `JWTAuthentication`:

```python
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    # request.user is automatically set
    user = request.user
```

## Sanitizing User Input

### HTML Sanitization

```python
from ano_backend.validators import sanitize_html

user_input = "<script>alert('xss')</script>Hello"
clean_input = sanitize_html(user_input)
# Result: "Hello"
```

### In Serializers

```python
from ano_backend.validators import sanitize_html

class MessageSerializer(serializers.ModelSerializer):
    def validate_content(self, value):
        # Sanitize HTML in message content
        return sanitize_html(value)
```

## Error Handling

### Consistent Error Format

```python
from rest_framework.response import Response
from rest_framework import status

# Validation error
return Response({
    'error': {
        'code': 'VALIDATION_ERROR',
        'message': 'Invalid input data',
        'details': {
            'email': ['Email is required'],
            'age': ['Age must be between 18 and 100']
        }
    }
}, status=status.HTTP_400_BAD_REQUEST)

# Authentication error
return Response({
    'error': {
        'code': 'AUTHENTICATION_FAILED',
        'message': 'Invalid credentials'
    }
}, status=status.HTTP_401_UNAUTHORIZED)

# Rate limit error
return Response({
    'error': {
        'code': 'RATE_LIMIT_EXCEEDED',
        'message': 'Too many requests',
        'retry_after': 300
    }
}, status=status.HTTP_429_TOO_MANY_REQUESTS)
```

## Testing Security

### Run Security Tests

```bash
python test_security.py
```

### Check Deployment Readiness

```bash
python manage.py check --deploy
```

### Test Specific Features

```python
# Test email validation
from ano_backend.validators import validate_iiti_email

try:
    validate_iiti_email('student@iiti.ac.in')
    print("Valid")
except ValueError as e:
    print(f"Invalid: {e}")

# Test file validation
from ano_backend.file_validators import validate_uploaded_file
from django.core.files.uploadedfile import SimpleUploadedFile

file = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
validate_uploaded_file(file, file_type='image')
```

## Common Patterns

### Protected API Endpoint

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ano_backend.validators import validate_request_data, validate_age

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@validate_request_data(
    required_fields=['age', 'interests'],
    field_validators={'age': validate_age}
)
def create_profile(request):
    data = request.data
    user = request.user
    # ... create profile
```

### File Upload Endpoint

```python
from ano_backend.file_validators import validate_uploaded_file
from django.core.exceptions import ValidationError

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    if 'avatar' not in request.FILES:
        return Response({'error': 'No file provided'}, status=400)
    
    file = request.FILES['avatar']
    
    try:
        validate_uploaded_file(file, file_type='image')
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)
    
    # Save file
    profile = request.user.profile
    profile.avatar = file
    profile.save()
    
    return Response({'message': 'Avatar uploaded successfully'})
```

### Search Endpoint with Sanitization

```python
from ano_backend.validators import sanitize_html

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    query = request.GET.get('q', '')
    
    # Sanitize search query
    clean_query = sanitize_html(query)
    
    # Perform search
    results = Message.objects.filter(content__icontains=clean_query)
    
    return Response(MessageSerializer(results, many=True).data)
```

## Environment Variables

### Development (.env)

```bash
DEBUG=True
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Production (.env)

```bash
DEBUG=False
SECRET_KEY=long-random-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

## Quick Checklist

Before committing code:

- [ ] Input validation on all user inputs
- [ ] File validation on all uploads
- [ ] CSRF token in frontend requests
- [ ] Authentication required on protected endpoints
- [ ] Error messages don't expose sensitive data
- [ ] No hardcoded secrets or passwords
- [ ] SQL queries use ORM (no raw SQL)
- [ ] User content sanitized before display
- [ ] Rate limiting on sensitive endpoints
- [ ] Tests pass: `python test_security.py`
