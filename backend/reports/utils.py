from django.db.models import Q
from .models import Block


def get_blocked_profile_ids(profile):
    """
    Get all profile IDs that are blocked by or have blocked the given profile.
    
    Args:
        profile: Profile instance
        
    Returns:
        Set of profile IDs that should be filtered out
    """
    blocked_by_user = Block.objects.filter(blocker=profile).values_list('blocked_id', flat=True)
    blocked_this_user = Block.objects.filter(blocked=profile).values_list('blocker_id', flat=True)
    
    blocked_ids = set(blocked_by_user) | set(blocked_this_user)
    
    return blocked_ids


def filter_blocked_profiles(queryset, profile):
    """
    Filter out blocked profiles from a queryset.
    
    Args:
        queryset: QuerySet of Profile objects
        profile: Profile instance to check blocks for
        
    Returns:
        Filtered queryset excluding blocked profiles
    """
    blocked_ids = get_blocked_profile_ids(profile)
    
    if blocked_ids:
        return queryset.exclude(id__in=blocked_ids)
    
    return queryset


def is_blocked(profile1, profile2):
    """
    Check if either profile has blocked the other.
    
    Args:
        profile1: First Profile instance
        profile2: Second Profile instance
        
    Returns:
        Boolean indicating if there's a block between the profiles
    """
    return Block.objects.filter(
        Q(blocker=profile1, blocked=profile2) |
        Q(blocker=profile2, blocked=profile1)
    ).exists()
