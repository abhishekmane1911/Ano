"""
File upload validation utilities.
Validates file types, sizes, and content to prevent malicious uploads.
"""
import os
from django.core.exceptions import ValidationError
from django.conf import settings

# Try to import magic, but make it optional
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available. Install libmagic for enhanced file validation.")


# Allowed file types with their MIME types
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp'],
}

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg': ['.mp3'],
    'audio/wav': ['.wav'],
    'audio/ogg': ['.ogg'],
    'audio/webm': ['.webm'],
}

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_AUDIO_SIZE = 5 * 1024 * 1024   # 5 MB


def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension against allowed list.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])
    
    Raises:
        ValidationError: If extension is not allowed
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
        )


def validate_file_size(file, max_size):
    """
    Validate file size.
    
    Args:
        file: File object
        max_size: Maximum size in bytes
    
    Raises:
        ValidationError: If file is too large
    """
    if file.size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            f'File size exceeds maximum allowed size of {max_size_mb:.1f} MB'
        )


def validate_file_mime_type(file, allowed_mime_types):
    """
    Validate file MIME type using python-magic.
    This checks the actual file content, not just the extension.
    Falls back to content_type if magic is not available.
    
    Args:
        file: File object
        allowed_mime_types: Dict of allowed MIME types
    
    Raises:
        ValidationError: If MIME type is not allowed
    """
    if MAGIC_AVAILABLE:
        # Read first 2048 bytes for MIME type detection
        file.seek(0)
        file_header = file.read(2048)
        file.seek(0)
        
        try:
            # Detect MIME type from file content
            mime = magic.from_buffer(file_header, mime=True)
            
            if mime not in allowed_mime_types:
                raise ValidationError(
                    f'File type not allowed. Detected type: {mime}'
                )
        except Exception as e:
            raise ValidationError(f'Could not validate file type: {str(e)}')
    else:
        # Fallback to content_type from upload
        mime = getattr(file, 'content_type', None)
        if mime and mime not in allowed_mime_types:
            raise ValidationError(
                f'File type not allowed. Detected type: {mime}'
            )


def validate_image_file(file):
    """
    Comprehensive validation for image uploads.
    
    Args:
        file: Uploaded file object
    
    Raises:
        ValidationError: If validation fails
    """
    # Validate file size first (before processing)
    validate_file_size(file, MAX_IMAGE_SIZE)
    
    # Get all allowed extensions
    allowed_extensions = []
    for extensions in ALLOWED_IMAGE_TYPES.values():
        allowed_extensions.extend(extensions)
    
    # Validate extension
    validate_file_extension(file.name, allowed_extensions)
    
    # Validate MIME type (checks actual file content)
    validate_file_mime_type(file, ALLOWED_IMAGE_TYPES)
    
    # Additional image-specific validation using Pillow
    try:
        from PIL import Image
        
        file.seek(0)
        img = Image.open(file)
        img.verify()  # Verify it's a valid image
        file.seek(0)
        
        # Check image dimensions (prevent extremely large images)
        img = Image.open(file)
        width, height = img.size
        max_dimension = 4096
        
        if width > max_dimension or height > max_dimension:
            raise ValidationError(
                f'Image dimensions too large. Maximum: {max_dimension}x{max_dimension}px'
            )
        
        # Check for minimum dimensions (prevent 1x1 pixel attacks)
        min_dimension = 10
        if width < min_dimension or height < min_dimension:
            raise ValidationError(
                f'Image dimensions too small. Minimum: {min_dimension}x{min_dimension}px'
            )
        
        # Check aspect ratio (prevent extremely wide/tall images)
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 10:
            raise ValidationError(
                'Image aspect ratio too extreme. Maximum ratio: 10:1'
            )
        
        file.seek(0)
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f'Invalid image file: {str(e)}')


def validate_audio_file(file):
    """
    Comprehensive validation for audio uploads.
    
    Args:
        file: Uploaded file object
    
    Raises:
        ValidationError: If validation fails
    """
    # Validate file size
    validate_file_size(file, MAX_AUDIO_SIZE)
    
    # Get all allowed extensions
    allowed_extensions = []
    for extensions in ALLOWED_AUDIO_TYPES.values():
        allowed_extensions.extend(extensions)
    
    # Validate extension
    validate_file_extension(file.name, allowed_extensions)
    
    # Validate MIME type
    validate_file_mime_type(file, ALLOWED_AUDIO_TYPES)


def scan_file_for_malware(file):
    """
    Placeholder for malware scanning.
    In production, integrate with ClamAV or similar antivirus solution.
    
    Args:
        file: Uploaded file object
    
    Raises:
        ValidationError: If malware is detected
    """
    # TODO: Integrate with ClamAV or cloud-based scanning service
    # For now, this is a placeholder that does basic checks
    
    file.seek(0)
    content = file.read(1024)  # Read first 1KB
    file.seek(0)
    
    # Check for common malware signatures (very basic)
    suspicious_patterns = [
        b'<?php',  # PHP code
        b'<script',  # JavaScript
        b'eval(',  # Eval functions
        b'exec(',  # Exec functions
    ]
    
    for pattern in suspicious_patterns:
        if pattern in content.lower():
            raise ValidationError(
                'File contains suspicious content and cannot be uploaded'
            )


def validate_uploaded_file(file, file_type='image'):
    """
    Main validation function for uploaded files.
    
    Args:
        file: Uploaded file object
        file_type: Type of file ('image' or 'audio')
    
    Raises:
        ValidationError: If validation fails
    """
    if not file:
        raise ValidationError('No file provided')
    
    # Validate based on file type
    if file_type == 'image':
        validate_image_file(file)
    elif file_type == 'audio':
        validate_audio_file(file)
    else:
        raise ValidationError(f'Unknown file type: {file_type}')
    
    # Scan for malware
    scan_file_for_malware(file)
