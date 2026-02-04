"""
File management utilities for media uploads.
"""
import os
import logging
from datetime import datetime, timedelta
from django.conf import settings
from chat.models import Message

logger = logging.getLogger(__name__)


def cleanup_orphaned_files():
    """
    Clean up orphaned media files that are not referenced in the database.
    This should be run periodically as a maintenance task.
    """
    cleaned_count = 0
    
    # Clean up chat media
    chat_media_path = os.path.join(settings.MEDIA_ROOT, 'chat_media')
    if os.path.exists(chat_media_path):
        cleaned_count += _cleanup_directory(chat_media_path, 'chat_media')
    
    # Clean up match media
    match_media_path = os.path.join(settings.MEDIA_ROOT, 'match_media')
    if os.path.exists(match_media_path):
        cleaned_count += _cleanup_directory(match_media_path, 'match_media')
    
    logger.info(f"Cleaned up {cleaned_count} orphaned files")
    return cleaned_count


def _cleanup_directory(directory_path, media_type):
    """Clean up files in a specific directory."""
    cleaned_count = 0
    
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Skip directories and temp files
            if not os.path.isfile(file_path) or filename.endswith('.tmp'):
                continue
            
            # Check if file is older than 24 hours and not referenced in DB
            file_stat = os.stat(file_path)
            file_age = datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)
            
            if file_age > timedelta(hours=24):
                media_url = f"/media/{media_type}/{filename}"
                
                # Check if file is referenced in any message
                if not Message.objects.filter(media_url__contains=filename).exists():
                    try:
                        os.unlink(file_path)
                        cleaned_count += 1
                        logger.info(f"Deleted orphaned file: {filename}")
                    except OSError as e:
                        logger.error(f"Failed to delete file {filename}: {e}")
    
    except OSError as e:
        logger.error(f"Failed to access directory {directory_path}: {e}")
    
    return cleaned_count


def get_file_info(file_path):
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict: File information including size, creation time, etc.
    """
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'exists': True
        }
    except OSError:
        return {'exists': False}


def validate_media_url(media_url):
    """
    Validate that a media URL points to an existing file.
    
    Args:
        media_url: The media URL to validate
        
    Returns:
        bool: True if file exists, False otherwise
    """
    if not media_url or not media_url.startswith('/media/'):
        return False
    
    # Extract relative path from URL
    relative_path = media_url.replace('/media/', '')
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    
    return os.path.isfile(full_path)