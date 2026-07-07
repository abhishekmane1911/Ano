"""
AI Moderation middleware for content interception and processing.
"""
import logging
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from .services import ModerationService
from .tasks import moderate_message_async

User = get_user_model()
logger = logging.getLogger(__name__)


class AIModerationMiddleware(MiddlewareMixin):
    """
    Middleware to intercept content creation and apply AI moderation.
    Processes POST requests to chat endpoints for real-time moderation.
    """
    
    # Endpoints that create content requiring moderation
    MODERATED_ENDPOINTS = [
        '/api/chat/messages/',
        '/api/chat/rooms/',
    ]
    
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Intercept requests to moderated endpoints and check content.
        For synchronous moderation of critical content.
        """
        # Only process POST requests to moderated endpoints
        if request.method != 'POST':
            return None
        
        # Skip authentication endpoints
        if '/auth/' in request.path:
            return None
        
        # Skip profile endpoints
        if '/profiles/' in request.path:
            return None
        
        # Skip admin endpoints
        if request.path.startswith('/admin/'):
            return None
            
        if not any(request.path.startswith(endpoint) for endpoint in self.MODERATED_ENDPOINTS):
            return None
        
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None
        
        try:
            # Parse request body to get content
            if hasattr(request, '_body') and request._body:
                body = json.loads(request.body.decode('utf-8'))
            else:
                # Try to read body if not cached
                body = json.loads(request.read().decode('utf-8'))
                # Reset the stream for Django to read again
                request._body = json.dumps(body).encode('utf-8')
            
            content = body.get('content', '')
            if not content:
                return None
            
            # Quick toxicity check for immediate rejection
            toxicity_score = self._quick_toxicity_check(content)
            
            # If content is highly toxic, reject immediately
            if toxicity_score >= 0.8:  # Higher threshold for immediate rejection
                logger.warning(f"Rejected high toxicity content from user {request.user.id}: {toxicity_score}")
                
                # Apply immediate penalties
                self._apply_immediate_penalties(request.user, toxicity_score, content)
                
                return JsonResponse({
                    'error': 'Content rejected due to policy violations',
                    'code': 'CONTENT_REJECTED',
                    'details': 'Your message contains inappropriate content and has been blocked.'
                }, status=400)
        
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            # If we can't parse the request, let it continue
            pass
        except Exception as e:
            logger.error(f"Error in AI moderation middleware: {e}")
            # Don't block requests if moderation fails
        
        return None
    
    def process_response(self, request, response):
        """
        Process response to trigger asynchronous moderation for approved content.
        """
        # Only process successful POST responses to moderated endpoints
        if (request.method == 'POST' and 
            response.status_code in [200, 201] and
            any(request.path.startswith(endpoint) for endpoint in self.MODERATED_ENDPOINTS)):
            
            try:
                # If response contains a message ID, queue for async moderation
                if hasattr(response, 'data') and isinstance(response.data, dict):
                    message_id = response.data.get('id')
                elif response.get('Content-Type', '').startswith('application/json'):
                    response_data = json.loads(response.content.decode('utf-8'))
                    message_id = response_data.get('id')
                else:
                    message_id = None
                
                if message_id:
                    # Queue message for detailed async moderation
                    moderate_message_async.delay(message_id)
                    logger.info(f"Queued message {message_id} for async moderation")
            
            except Exception as e:
                logger.error(f"Error queuing message for async moderation: {e}")
        
        return response
    
    def _quick_toxicity_check(self, content: str) -> float:
        """
        Perform quick toxicity check for immediate rejection.
        This is a simplified check - full moderation happens asynchronously.
        """
        # Simple keyword-based check for immediate rejection
        high_toxicity_keywords = [
            'kill yourself', 'kys', 'suicide', 'die', 'murder',
            'rape', 'assault', 'violence', 'harm', 'hurt',
            # Add more keywords as needed
        ]
        
        content_lower = content.lower()
        for keyword in high_toxicity_keywords:
            if keyword in content_lower:
                return 0.9  # High toxicity score
        
        # Check for excessive profanity or caps
        if self._has_excessive_profanity(content) or self._is_excessive_caps(content):
            return 0.7
        
        return 0.1  # Default low toxicity
    
    def _has_excessive_profanity(self, content: str) -> bool:
        """Check for excessive profanity in content."""
        # Simple profanity check - can be enhanced with better-profanity library
        profanity_words = ['fuck', 'shit', 'damn', 'bitch', 'asshole']  # Basic list
        content_lower = content.lower()
        profanity_count = sum(1 for word in profanity_words if word in content_lower)
        return profanity_count > 2  # More than 2 profane words
    
    def _is_excessive_caps(self, content: str) -> bool:
        """Check if content has excessive capital letters."""
        if len(content) < 10:
            return False
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
        return caps_ratio > 0.7  # More than 70% caps
    
    def _apply_immediate_penalties(self, user: User, toxicity_score: float, content: str):
        """Apply immediate penalties for high toxicity content."""
        try:
            # Create violation record
            from .models import ViolationHistory
            ViolationHistory.objects.create(
                user=user,
                violation_type='toxicity',
                toxicity_score=toxicity_score,
                content_snippet=content[:200],
                action_taken='immediate_rejection'
            )
            
            # Apply shadowban
            ModerationService._apply_shadowban(
                user, 
                24, 
                f"Immediate rejection for high toxicity (score: {toxicity_score})"
            )
            
            # Deduct reputation points
            from reputation.services import ReputationService
            ReputationService.award_points(user, 'validated_report')
            
        except Exception as e:
            logger.error(f"Error applying immediate penalties: {e}")