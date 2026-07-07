"""
Middleware for tier-based privilege enforcement and real-time tier updates.
"""

import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from .services import TierPrivilegeManager, ReputationService

User = get_user_model()


class TierPrivilegeMiddleware(MiddlewareMixin):
    """
    Middleware to handle tier-based privilege enforcement and real-time tier updates.
    
    This middleware:
    1. Checks for tier updates after reputation changes
    2. Adds tier information to request context
    3. Handles privilege-based access control for specific endpoints
    """
    
    # Endpoints that require specific privileges
    PRIVILEGE_ENDPOINTS = {
        '/api/reputation/vote/': 'vote',
        '/api/chat/upload-image/': 'upload_images',
        '/api/chat/create-poll/': 'create_polls',
        '/api/chat/create-confession/': 'create_confessions',
    }
    
    def process_request(self, request):
        """
        Process incoming request to add tier information and check privileges.
        """
        # Skip processing for unauthenticated users
        if not request.user.is_authenticated:
            return None
        
        # Add tier information to request for easy access in views
        reputation = ReputationService.get_or_create_reputation(request.user)
        request.user_tier = reputation.rank_tier
        request.user_reputation_score = reputation.reputation_score
        request.user_privileges = TierPrivilegeManager.get_user_privileges(request.user)
        
        # Check if this endpoint requires specific privileges
        path = request.path
        required_privilege = self.PRIVILEGE_ENDPOINTS.get(path)
        
        if required_privilege:
            if not TierPrivilegeManager.check_user_privilege(request.user, required_privilege):
                privilege_info = TierPrivilegeManager.get_privilege_info(request.user, required_privilege)
                
                # Return JSON error for API endpoints
                if path.startswith('/api/'):
                    return JsonResponse({
                        'error': f'Insufficient privileges. {required_privilege} requires {privilege_info["required_tier"]} tier or higher.',
                        'code': 'INSUFFICIENT_PRIVILEGES',
                        'details': {
                            'required_action': required_privilege,
                            'required_tier': privilege_info['required_tier'],
                            'current_tier': privilege_info['current_tier'],
                            'current_score': privilege_info['current_score'],
                            'message': f'Earn more reputation to unlock {required_privilege} privileges!'
                        }
                    }, status=403)
        
        return None
    
    def process_response(self, request, response):
        """
        Process response to add tier update information if needed.
        """
        # Skip processing for unauthenticated users or non-JSON responses
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # Check if this was a reputation-affecting action
        if (hasattr(request, 'reputation_updated') and 
            request.reputation_updated and 
            response.status_code == 200):
            
            # Get current tier information
            tier_info = ReputationService.update_user_tier_realtime(request.user)
            
            # If response is JSON and tier changed, add tier update info
            if (response.get('Content-Type', '').startswith('application/json') and 
                tier_info['tier_changed']):
                
                try:
                    # Parse existing response
                    response_data = json.loads(response.content.decode('utf-8'))
                    
                    # Add tier update information
                    response_data['tier_update'] = {
                        'tier_changed': True,
                        'old_tier': tier_info['old_tier'],
                        'new_tier': tier_info['new_tier'],
                        'new_privileges': tier_info['new_privileges'],
                        'tier_upgrade': tier_info['tier_upgrade'],
                        'message': f"Congratulations! You've been promoted to {tier_info['new_tier']}!" if tier_info['tier_upgrade'] else f"Your tier has been updated to {tier_info['new_tier']}"
                    }
                    
                    # Update response content
                    response.content = json.dumps(response_data).encode('utf-8')
                    
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If we can't parse the response, just continue
                    pass
        
        return response


class ReputationTrackingMixin:
    """
    Mixin for views that affect user reputation.
    Marks the request for tier update checking in middleware.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Mark request as potentially affecting reputation"""
        request.reputation_updated = True
        return super().dispatch(request, *args, **kwargs)


def add_tier_context(request):
    """
    Context processor to add tier information to template context.
    
    Usage in settings.py:
    TEMPLATES = [{
        'OPTIONS': {
            'context_processors': [
                'reputation.middleware.add_tier_context',
                # ... other context processors
            ],
        },
    }]
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        reputation = ReputationService.get_or_create_reputation(request.user)
        return {
            'user_tier': reputation.rank_tier,
            'user_reputation_score': reputation.reputation_score,
            'user_level': reputation.calculate_level(),
            'user_privileges': TierPrivilegeManager.get_user_privileges(request.user),
            'xp_for_next_level': reputation.xp_for_next_level(),
        }
    return {}