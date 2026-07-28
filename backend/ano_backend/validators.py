"""
Input validation decorators and utilities for API endpoints.
Provides reusable validation logic to prevent injection attacks and invalid data.
"""
from functools import wraps
from django.http import JsonResponse
from rest_framework import status
import re


def validate_request_data(required_fields=None, optional_fields=None, field_validators=None):
    """
    Decorator to validate request data before processing.
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
        field_validators: Dict mapping field names to validation functions
    
    Example:
        @validate_request_data(
            required_fields=['email', 'password'],
            field_validators={'email': validate_email}
        )
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if hasattr(request, 'data'):
                data = request.data
            else:
                data = request.POST or {}
            
            errors = {}
            
            if required_fields:
                for field in required_fields:
                    if field not in data or data[field] in [None, '', []]:
                        errors[field] = [f'{field} is required']
            
            # val field values
            if field_validators:
                for field, validator in field_validators.items():
                    if field in data and data[field] not in [None, '']:
                        try:
                            validator(data[field])
                        except ValueError as e:
                            errors[field] = [str(e)]
            
            # Check for unexpected fields (prevent mass assignment)
            if required_fields or optional_fields:
                allowed_fields = set(required_fields or []) | set(optional_fields or [])
                unexpected_fields = set(data.keys()) - allowed_fields
                if unexpected_fields:
                    errors['_unexpected'] = [
                        f'Unexpected fields: {", ".join(unexpected_fields)}'
                    ]
            
            if errors:
                return JsonResponse({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid input data',
                        'details': errors
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def validate_email(email):
    if not isinstance(email, str):
        raise ValueError('Email must be a string')
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError('Invalid email format')
    
    if len(email) > 254:
        raise ValueError('Email is too long')


def validate_iiti_email(email):
    validate_email(email)
    if not email.endswith('@iiti.ac.in'):
        raise ValueError('Email must be from @iiti.ac.in domain')


def validate_password(password):
    if not isinstance(password, str):
        raise ValueError('Password must be a string')
    
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    
    if len(password) > 128:
        raise ValueError('Password is too long')
    
    if not re.search(r'[a-zA-Z]', password):
        raise ValueError('Password must contain at least one letter')
    
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one number')


def validate_uuid(value):
    if not isinstance(value, str):
        raise ValueError('UUID must be a string')
    
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, value.lower()):
        raise ValueError('Invalid UUID format')


def validate_age(age):
    """Validate age is within acceptable range"""
    try:
        age_int = int(age)
    except (ValueError, TypeError):
        raise ValueError('Age must be a number')
    
    if age_int < 18 or age_int > 100:
        raise ValueError('Age must be between 18 and 100')


def validate_text_length(text, min_length=0, max_length=None):
    """Validate text length"""
    if not isinstance(text, str):
        raise ValueError('Text must be a string')
    
    if len(text) < min_length:
        raise ValueError(f'Text must be at least {min_length} characters')
    
    if max_length and len(text) > max_length:
        raise ValueError(f'Text must not exceed {max_length} characters')


def validate_choice(value, choices):
    """Validate value is in allowed choices"""
    if value not in choices:
        raise ValueError(f'Value must be one of: {", ".join(choices)}')


def sanitize_html(text):
    """
    Remove potentially dangerous HTML/script tags from text.
    Basic XSS prevention for user-generated content.
    """
    if not isinstance(text, str):
        return text
    
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove event handlers
    text = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*on\w+\s*=\s*\S+', '', text, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    return text


def validate_json_array(value, item_validator=None, max_items=None):
    """Validate JSON array field"""
    if not isinstance(value, list):
        raise ValueError('Value must be an array')
    
    if max_items and len(value) > max_items:
        raise ValueError(f'Array must not contain more than {max_items} items')
    
    if item_validator:
        for i, item in enumerate(value):
            try:
                item_validator(item)
            except ValueError as e:
                raise ValueError(f'Item {i}: {str(e)}')
