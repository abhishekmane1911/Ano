import math
from typing import Optional, List, Dict, Any
from functools import wraps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from .models import UserReputation, Vote, MessageRanking
from chat.models import Message

User = get_user_model()


class TierPrivilegeManager:
    """
    Manager for tier-based privilege system.
    Handles privilege checking and enforcement based on user reputation tiers.
    """
    
    # Define tier privileges according to requirements 2.1-2.4
    TIER_PRIVILEGES = {
        'Fresher': ['read', 'write'],
        'Sophomore': ['read', 'write', 'vote'],
        'Senior': ['read', 'write', 'vote', 'upload_images'],
        'Campus Legend': ['read', 'write', 'vote', 'upload_images', 'create_polls', 'create_confessions']
    }
    
    # Reverse mapping for quick lookup of required tier for actions
    ACTION_TIER_REQUIREMENTS = {
        'read': 'Fresher',
        'write': 'Fresher',
        'vote': 'Sophomore',
        'upload_images': 'Senior',
        'create_polls': 'Campus Legend',
        'create_confessions': 'Campus Legend'
    }
    
    @classmethod
    def has_privilege(cls, user_tier: str, action: str) -> bool:
        """
        Check if a user tier has privilege for a specific action.
        
        Args:
            user_tier: User's current tier (Fresher, Sophomore, Senior, Campus Legend)
            action: Action to check privilege for
            
        Returns:
            bool: True if user has privilege, False otherwise
        """
        return action in cls.TIER_PRIVILEGES.get(user_tier, [])
    
    @classmethod
    def get_required_tier(cls, action: str) -> str:
        """
        Get the minimum tier required for an action.
        
        Args:
            action: Action to check
            
        Returns:
            str: Minimum tier required for the action
        """
        return cls.ACTION_TIER_REQUIREMENTS.get(action, 'Campus Legend')
    
    @classmethod
    def get_user_privileges(cls, user: User) -> List[str]:
        """
        Get all privileges for a user based on their current tier.
        
        Args:
            user: User instance
            
        Returns:
            List[str]: List of privileges the user has
        """
        reputation = ReputationService.get_or_create_reputation(user)
        return cls.TIER_PRIVILEGES.get(reputation.rank_tier, [])
    
    @classmethod
    def check_user_privilege(cls, user: User, action: str) -> bool:
        """
        Check if a user has privilege for a specific action.
        
        Args:
            user: User instance
            action: Action to check privilege for
            
        Returns:
            bool: True if user has privilege, False otherwise
        """
        reputation = ReputationService.get_or_create_reputation(user)
        return cls.has_privilege(reputation.rank_tier, action)
    
    @classmethod
    def get_privilege_info(cls, user: User, action: str) -> Dict[str, Any]:
        """
        Get detailed privilege information for a user and action.
        
        Args:
            user: User instance
            action: Action to check
            
        Returns:
            Dict containing privilege status, current tier, required tier, etc.
        """
        reputation = ReputationService.get_or_create_reputation(user)
        has_privilege = cls.has_privilege(reputation.rank_tier, action)
        required_tier = cls.get_required_tier(action)
        
        return {
            'has_privilege': has_privilege,
            'current_tier': reputation.rank_tier,
            'required_tier': required_tier,
            'current_score': reputation.reputation_score,
            'action': action,
            'all_privileges': cls.TIER_PRIVILEGES.get(reputation.rank_tier, [])
        }


def require_privilege(action: str, return_json: bool = False):
    """
    Decorator to enforce tier-based privileges on views.
    
    Args:
        action: The privilege action required (e.g., 'vote', 'upload_images')
        return_json: If True, return JSON response for API views, else Django HttpResponse
        
    Usage:
        @require_privilege('vote')
        def vote_view(request):
            # View logic here
            pass
            
        @require_privilege('upload_images', return_json=True)
        @api_view(['POST'])
        def upload_image_api(request):
            # API view logic here
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                if return_json:
                    return JsonResponse({
                        'error': 'Authentication required',
                        'code': 'AUTHENTICATION_REQUIRED'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    from django.contrib.auth.decorators import login_required
                    return login_required(view_func)(request, *args, **kwargs)
            
            # Check user privilege
            if not TierPrivilegeManager.check_user_privilege(request.user, action):
                privilege_info = TierPrivilegeManager.get_privilege_info(request.user, action)
                
                error_response = {
                    'error': f'Insufficient privileges. {action} requires {privilege_info["required_tier"]} tier or higher.',
                    'code': 'INSUFFICIENT_PRIVILEGES',
                    'details': {
                        'required_action': action,
                        'required_tier': privilege_info['required_tier'],
                        'current_tier': privilege_info['current_tier'],
                        'current_score': privilege_info['current_score']
                    }
                }
                
                if return_json:
                    return JsonResponse(error_response, status=status.HTTP_403_FORBIDDEN)
                else:
                    from django.http import HttpResponseForbidden
                    return HttpResponseForbidden(f"Access denied: {error_response['error']}")
            
            # User has privilege, proceed with view
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_privilege_drf(action: str):
    """
    Decorator specifically for Django REST Framework views.
    Returns DRF Response objects with proper error formatting.
    
    Args:
        action: The privilege action required
        
    Usage:
        @require_privilege_drf('vote')
        @api_view(['POST'])
        def vote_api_view(request):
            # API view logic here
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # Handle both function-based views and ViewSet methods
            if len(args) > 0 and hasattr(args[0], 'request'):
                # ViewSet method - first arg is self, request is self.request
                request = args[0].request
            elif len(args) > 0 and hasattr(args[0], 'user'):
                # Function-based view - first arg is request
                request = args[0]
            else:
                # Fallback - assume first arg is request
                request = args[0] if args else None
            
            if not request:
                return Response({
                    'error': 'Invalid request',
                    'code': 'INVALID_REQUEST'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Authentication required',
                    'code': 'AUTHENTICATION_REQUIRED'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check user privilege
            if not TierPrivilegeManager.check_user_privilege(request.user, action):
                privilege_info = TierPrivilegeManager.get_privilege_info(request.user, action)
                
                return Response({
                    'error': f'Insufficient privileges. {action} requires {privilege_info["required_tier"]} tier or higher.',
                    'code': 'INSUFFICIENT_PRIVILEGES',
                    'details': {
                        'required_action': action,
                        'required_tier': privilege_info['required_tier'],
                        'current_tier': privilege_info['current_tier'],
                        'current_score': privilege_info['current_score'],
                        'message': f'Earn more reputation to unlock {action} privileges!'
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # User has privilege, proceed with view
            return view_func(*args, **kwargs)
        
        return wrapper
    return decorator


class ReputationService:
    """Service for managing user reputation and points"""
    
    # Point values for different actions
    POINTS = {
        'post_upvote': 5,
        'comment_upvote': 2,
        'post_downvote': -2,
        'comment_downvote': -2,
        'message_upvote': 5,  # Backward compatibility
        'message_downvote': -2,  # Backward compatibility
        'validated_report': -50,
    }
    
    @classmethod
    def get_or_create_reputation(cls, user: User) -> UserReputation:
        """Get or create user reputation"""
        reputation, created = UserReputation.objects.get_or_create(user=user)
        return reputation
    
    @classmethod
    def award_points(cls, user: User, action: str, points: Optional[int] = None) -> Dict[str, Any]:
        """
        Award points to user for an action and handle real-time tier updates.
        
        Returns:
            Dict containing updated reputation info and any tier changes
        """
        if points is None:
            points = cls.POINTS.get(action, 0)
        
        with transaction.atomic():
            reputation = cls.get_or_create_reputation(user)
            old_tier = reputation.rank_tier
            old_score = reputation.reputation_score
            
            # Update reputation score
            reputation.reputation_score += points
            reputation.save()
            
            # Update tier based on new score (real-time update)
            new_tier = reputation.update_tier()
            
            # Check if tier changed
            tier_changed = old_tier != new_tier
            
            # Prepare response with tier update info
            result = {
                'user_id': str(user.id),
                'old_score': old_score,
                'new_score': reputation.reputation_score,
                'points_awarded': points,
                'old_tier': old_tier,
                'new_tier': new_tier,
                'tier_changed': tier_changed,
                'action': action,
                'level': reputation.calculate_level(),
                'xp_for_next_level': reputation.xp_for_next_level()
            }
            
            # Add privilege information if tier changed
            if tier_changed:
                new_privileges = TierPrivilegeManager.get_user_privileges(user)
                tier_upgrade = cls._get_tier_hierarchy().index(new_tier) > cls._get_tier_hierarchy().index(old_tier)
                
                result['new_privileges'] = new_privileges
                result['tier_upgrade'] = tier_upgrade
                
                # Add tier update data for WebSocket broadcasting
                result['tier_update'] = {
                    'user_id': str(user.id),
                    'old_tier': old_tier,
                    'new_tier': new_tier,
                    'new_privileges': new_privileges,
                    'tier_upgrade': tier_upgrade
                }
            
            return result
    
    @classmethod
    def _get_tier_hierarchy(cls) -> List[str]:
        """Get tier hierarchy in ascending order"""
        return ['Fresher', 'Sophomore', 'Senior', 'Campus Legend']
    
    @classmethod
    def update_user_tier_realtime(cls, user: User) -> Dict[str, Any]:
        """
        Force real-time tier update for a user.
        Used when reputation changes outside of normal point awarding.
        
        Returns:
            Dict containing tier update information
        """
        with transaction.atomic():
            reputation = cls.get_or_create_reputation(user)
            old_tier = reputation.rank_tier
            
            # Force tier recalculation
            new_tier = reputation.update_tier()
            
            tier_changed = old_tier != new_tier
            
            result = {
                'old_tier': old_tier,
                'new_tier': new_tier,
                'tier_changed': tier_changed,
                'current_score': reputation.reputation_score,
                'user_id': str(user.id)
            }
            
            if tier_changed:
                result['new_privileges'] = TierPrivilegeManager.get_user_privileges(user)
                result['tier_upgrade'] = cls._get_tier_hierarchy().index(new_tier) > cls._get_tier_hierarchy().index(old_tier)
            
            return result
    
    @classmethod
    def check_tier_privileges(cls, user: User, action: str) -> bool:
        """
        Check if user has privilege for action based on tier.
        Delegates to TierPrivilegeManager for consistency.
        """
        return TierPrivilegeManager.check_user_privilege(user, action)
    
    @classmethod
    def apply_report_penalty(cls, user: User) -> Dict[str, Any]:
        """Apply penalty when user's report is validated by moderators"""
        return cls.award_points(user, 'validated_report')
    
    @classmethod
    def get_user_level(cls, user: User) -> int:
        """Get user's current level"""
        reputation = cls.get_or_create_reputation(user)
        return reputation.calculate_level()
    
    @classmethod
    def get_xp_for_next_level(cls, user: User) -> float:
        """Get XP needed for user's next level"""
        reputation = cls.get_or_create_reputation(user)
        return reputation.xp_for_next_level()


class WilsonScoreCalculator:
    """Service for calculating Wilson Scores for content ranking"""
    
    @staticmethod
    def calculate_score(upvotes: int, total_votes: int, confidence: float = 0.95) -> float:
        """Calculate Wilson Score Interval lower bound"""
        if total_votes == 0:
            return 0.0
        
        p = upvotes / total_votes
        z = 1.96  # 95% confidence interval
        
        numerator = p + (z * z) / (2 * total_votes) - z * math.sqrt((p * (1 - p) + (z * z) / (4 * total_votes)) / total_votes)
        denominator = 1 + (z * z) / total_votes
        
        return numerator / denominator
    
    @classmethod
    def update_message_ranking(cls, message: Message) -> float:
        """Update Wilson Score for a message"""
        ranking, created = MessageRanking.objects.get_or_create(message=message)
        ranking.update_wilson_score()
        return ranking.wilson_score


class VotingService:
    """Service for handling votes on messages"""
    
    @classmethod
    def cast_vote(cls, user: User, message: Message, vote_type: str) -> Dict[str, Any]:
        """Cast or update a vote on a message"""
        if not ReputationService.check_tier_privileges(user, 'vote'):
            return {
                'success': False,
                'error': 'Insufficient privileges for voting',
                'privilege_info': TierPrivilegeManager.get_privilege_info(user, 'vote')
            }
        
        with transaction.atomic():
            # Get existing vote
            try:
                vote = Vote.objects.get(user=user, message=message)
                existing_vote = vote.vote_type
            except Vote.DoesNotExist:
                vote = None
                existing_vote = None

            points_to_award = 0
            
            if existing_vote == vote_type:
                # User clicked the same vote button -> Toggle OFF
                vote.delete()
                # Revert points
                if existing_vote == 'upvote':
                    points_to_award = -ReputationService.POINTS['post_upvote']
                else:
                    points_to_award = -ReputationService.POINTS['post_downvote']
                final_vote_type = None
            else:
                if vote is None:
                    # New vote
                    vote = Vote.objects.create(user=user, message=message, vote_type=vote_type)
                    if vote_type == 'upvote':
                        points_to_award = ReputationService.POINTS['post_upvote']
                    else:
                        points_to_award = ReputationService.POINTS['post_downvote']
                else:
                    # Switch vote
                    vote.vote_type = vote_type
                    vote.save()
                    if vote_type == 'upvote':
                        points_to_award = ReputationService.POINTS['post_upvote'] - ReputationService.POINTS['post_downvote']
                    else:
                        points_to_award = ReputationService.POINTS['post_downvote'] - ReputationService.POINTS['post_upvote']
                final_vote_type = vote_type
            
            # Update message ranking
            ranking_data = cls._update_message_votes(message)
            
            # Award points to message author
            if points_to_award != 0:
                point_result = ReputationService.award_points(message.sender.user, 'post_upvote', points=points_to_award)
            else:
                reputation = ReputationService.get_or_create_reputation(message.sender.user)
                point_result = {
                    'user_id': str(message.sender.user.id),
                    'old_score': reputation.reputation_score,
                    'new_score': reputation.reputation_score,
                    'points_awarded': 0,
                    'old_tier': reputation.rank_tier,
                    'new_tier': reputation.rank_tier,
                    'tier_changed': False,
                    'action': 'vote_unchanged',
                    'level': reputation.calculate_level(),
                    'xp_for_next_level': reputation.xp_for_next_level()
                }
            
            # Broadcast real-time updates
            cls._broadcast_updates(message, ranking_data, point_result)
            
            # Return vote result with any tier changes
            result = {
                'success': True,
                'vote_type': final_vote_type,
                'ranking_data': ranking_data,
                'reputation_update': point_result
            }
            
            # Include tier update if it occurred
            if point_result and 'tier_update' in point_result:
                result['tier_update'] = point_result['tier_update']
            
            return result
    
    @classmethod
    def _update_message_votes(cls, message: Message) -> Dict[str, Any]:
        """Update vote counts for a message and return ranking data"""
        votes = Vote.objects.filter(message=message)
        upvotes = votes.filter(vote_type='upvote').count()
        downvotes = votes.filter(vote_type='downvote').count()
        
        ranking, created = MessageRanking.objects.get_or_create(message=message)
        ranking.upvotes = upvotes
        ranking.downvotes = downvotes
        ranking.update_wilson_score()
        
        total_votes = upvotes + downvotes
        upvote_percentage = (upvotes / total_votes * 100) if total_votes > 0 else 0.0
        
        return {
            'upvotes': upvotes,
            'downvotes': downvotes,
            'total_votes': total_votes,
            'wilson_score': round(ranking.wilson_score, 4),
            'upvote_percentage': round(upvote_percentage, 1)
        }
    
    @classmethod
    def _broadcast_updates(cls, message: Message, ranking_data: Dict[str, Any], point_result: Dict[str, Any]):
        """Broadcast real-time updates via WebSocket"""
        try:
            from .websocket_utils import realtime_notifier
            
            # Broadcast ranking update
            chatroom_id = str(message.chatroom.id) if message.chatroom else None
            match_id = str(message.match.id) if message.match else None
            
            realtime_notifier.broadcast_ranking_update(
                message_id=str(message.id),
                ranking_data=ranking_data,
                chatroom_id=chatroom_id,
                match_id=match_id
            )
            
            # Broadcast reputation update if points were awarded
            if point_result and 'user_id' in point_result:
                realtime_notifier.broadcast_reputation_update(
                    user_id=point_result['user_id'],
                    reputation_data=point_result,
                    chatroom_id=chatroom_id
                )
            
            # Broadcast tier update if tier changed
            if point_result and 'tier_update' in point_result:
                tier_data = point_result['tier_update']
                realtime_notifier.broadcast_tier_update(
                    user_id=tier_data.get('user_id'),
                    old_tier=tier_data.get('old_tier'),
                    new_tier=tier_data.get('new_tier'),
                    new_privileges=tier_data.get('new_privileges', []),
                    chatroom_id=chatroom_id
                )
        except ImportError:
            # WebSocket utilities not available, skip broadcasting
            pass