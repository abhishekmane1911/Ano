import logging
import os
from typing import Dict, List, Optional, Tuple
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import ModerationResult, ViolationHistory, Shadowban
from chat.models import Message

# Import monitoring and circuit breaker functionality
from ano_backend.monitoring import (
    openai_circuit_breaker, 
    monitor_async_operation,
    with_circuit_breaker,
    CircuitBreakerOpenException
)

# AI Moderation imports
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from better_profanity import profanity
    PROFANITY_AVAILABLE = True
except ImportError:
    PROFANITY_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

User = get_user_model()
logger = logging.getLogger(__name__)


class HeatSystem:
    """
    Advanced heat tracking system for repeat offenders.
    Implements escalating penalties and rehabilitation mechanisms.
    """
    
    # Heat level thresholds
    HEAT_LEVELS = {
        0: {'name': 'Clean', 'multiplier': 1.0, 'max_violations': 0},
        1: {'name': 'Warm', 'multiplier': 1.2, 'max_violations': 1},
        2: {'name': 'Hot', 'multiplier': 1.5, 'max_violations': 3},
        3: {'name': 'Burning', 'multiplier': 2.0, 'max_violations': 5},
        4: {'name': 'Scorching', 'multiplier': 3.0, 'max_violations': 8},
        5: {'name': 'Inferno', 'multiplier': 5.0, 'max_violations': float('inf')},
    }
    
    # Rehabilitation parameters
    REHABILITATION_PERIOD_DAYS = 14  # Days of good behavior to reduce heat
    GOOD_BEHAVIOR_THRESHOLD = 10    # Positive actions needed for rehabilitation
    
    @classmethod
    def get_user_heat_level(cls, user: User) -> int:
        """Calculate user's current heat level based on recent violations"""
        # Get violations from the last 30 days
        recent_violations = ViolationHistory.objects.filter(
            user=user,
            is_active=True,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')
        
        violation_count = recent_violations.count()
        
        # Determine heat level based on violation count
        for level in range(5, -1, -1):  # Check from highest to lowest
            if violation_count >= cls.HEAT_LEVELS[level]['max_violations']:
                return level
        
        return 0  # Clean slate
    
    @classmethod
    def get_heat_info(cls, user: User) -> Dict:
        """Get comprehensive heat information for a user"""
        heat_level = cls.get_user_heat_level(user)
        heat_info = cls.HEAT_LEVELS[heat_level].copy()
        
        # Get recent violations
        recent_violations = ViolationHistory.objects.filter(
            user=user,
            is_active=True,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Calculate rehabilitation progress
        rehabilitation_progress = cls._calculate_rehabilitation_progress(user)
        
        # Get active shadowban info
        active_shadowban = Shadowban.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        
        return {
            'heat_level': heat_level,
            'heat_name': heat_info['name'],
            'penalty_multiplier': heat_info['multiplier'],
            'recent_violations': recent_violations,
            'rehabilitation_progress': rehabilitation_progress,
            'is_shadowbanned': bool(active_shadowban),
            'shadowban_expires': active_shadowban.expires_at if active_shadowban else None,
            'next_level_violations': cls._get_next_level_threshold(heat_level),
            'can_rehabilitate': rehabilitation_progress >= 100
        }
    
    @classmethod
    def _calculate_rehabilitation_progress(cls, user: User) -> float:
        """Calculate rehabilitation progress as a percentage (0-100)"""
        # Check for good behavior in the last rehabilitation period
        cutoff_date = timezone.now() - timedelta(days=cls.REHABILITATION_PERIOD_DAYS)
        
        # Count positive actions (this would need to be implemented based on your app's actions)
        # For now, we'll use a simple metric: days without violations
        last_violation = ViolationHistory.objects.filter(
            user=user,
            created_at__gte=cutoff_date
        ).order_by('-created_at').first()
        
        if not last_violation:
            # No violations in rehabilitation period
            days_clean = cls.REHABILITATION_PERIOD_DAYS
        else:
            # Calculate days since last violation
            days_clean = (timezone.now() - last_violation.created_at).days
        
        # Calculate progress percentage
        progress = min((days_clean / cls.REHABILITATION_PERIOD_DAYS) * 100, 100)
        return progress
    
    @classmethod
    def _get_next_level_threshold(cls, current_level: int) -> Optional[int]:
        """Get the number of violations needed to reach the next heat level"""
        if current_level >= 5:
            return None  # Already at maximum level
        
        next_level = current_level + 1
        return cls.HEAT_LEVELS[next_level]['max_violations']
    
    @classmethod
    def apply_heat_penalty(cls, user: User, base_duration_hours: int, toxicity_score: float) -> int:
        """Apply heat-based penalty multiplier to base duration"""
        heat_level = cls.get_user_heat_level(user)
        multiplier = cls.HEAT_LEVELS[heat_level]['multiplier']
        
        # Additional multiplier based on toxicity score
        toxicity_multiplier = 1 + (toxicity_score - 0.7) * 2
        
        # Calculate final duration
        final_duration = int(base_duration_hours * multiplier * toxicity_multiplier)
        
        # Cap at reasonable maximum (1 week)
        final_duration = min(final_duration, 168)
        
        logger.info(f"Heat penalty applied - Level: {heat_level}, Base: {base_duration_hours}h, "
                   f"Multiplier: {multiplier}, Final: {final_duration}h")
        
        return final_duration
    
    @classmethod
    def attempt_rehabilitation(cls, user: User) -> bool:
        """Attempt to rehabilitate user by reducing their heat level"""
        heat_info = cls.get_heat_info(user)
        
        if not heat_info['can_rehabilitate']:
            return False
        
        # Deactivate oldest violations to reduce heat level
        old_violations = ViolationHistory.objects.filter(
            user=user,
            is_active=True
        ).order_by('created_at')[:2]  # Deactivate 2 oldest violations
        
        count = old_violations.count()
        old_violations.update(is_active=False)
        
        logger.info(f"Rehabilitated user {user.id}: deactivated {count} old violations")
        return count > 0
    
    @classmethod
    def get_escalation_warning(cls, user: User) -> Optional[str]:
        """Get warning message about potential escalation"""
        heat_info = cls.get_heat_info(user)
        heat_level = heat_info['heat_level']
        
        if heat_level == 0:
            return None
        elif heat_level == 1:
            return "You're on thin ice. Another violation may result in longer penalties."
        elif heat_level == 2:
            return "Multiple violations detected. Future penalties will be significantly increased."
        elif heat_level == 3:
            return "Serious violation pattern detected. You're at risk of extended restrictions."
        elif heat_level == 4:
            return "Critical violation level reached. Next violation may result in severe penalties."
        else:  # heat_level == 5
            return "Maximum penalty level reached. All future violations will receive the harshest penalties."


class OpenAIModerator:
    """OpenAI-based content moderation service with circuit breaker protection"""
    
    def __init__(self):
        self.client = None
        self.available = OPENAI_AVAILABLE
        
        if self.available:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    self.client = OpenAI(api_key=api_key)
                    logger.info("OpenAI moderator initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")
                    self.available = False
            else:
                logger.warning("OpenAI API key not found in environment variables")
                self.available = False
    
    @monitor_async_operation("openai_moderation")
    def check_content(self, content: str) -> Dict:
        """
        Check content using OpenAI Moderation API with circuit breaker protection
        Returns: {
            'flagged': bool,
            'categories': List[str],
            'toxicity_score': float,
            'category_scores': Dict[str, float]
        }
        """
        if not self.available or not self.client:
            return {
                'flagged': False,
                'categories': [],
                'toxicity_score': 0.0,
                'category_scores': {},
                'error': 'OpenAI not available'
            }
        
        try:
            # Use circuit breaker for OpenAI API calls
            return openai_circuit_breaker.call(self._make_openai_request, content)
            
        except CircuitBreakerOpenException as e:
            logger.warning(f"OpenAI circuit breaker is open: {e}")
            return {
                'flagged': False,
                'categories': [],
                'toxicity_score': 0.0,
                'category_scores': {},
                'error': 'OpenAI service temporarily unavailable'
            }
        except Exception as e:
            logger.error(f"OpenAI moderation error: {e}")
            return {
                'flagged': False,
                'categories': [],
                'toxicity_score': 0.0,
                'category_scores': {},
                'error': str(e)
            }
    
    def _make_openai_request(self, content: str) -> Dict:
        """Make the actual OpenAI API request (protected by circuit breaker)"""
        response = self.client.moderations.create(input=content)
        result = response.results[0]
        
        # Extract flagged categories
        flagged_categories = []
        category_scores = {}
        
        for category, flagged in result.categories.model_dump().items():
            if flagged:
                flagged_categories.append(category)
        
        # Get category scores
        for category, score in result.category_scores.model_dump().items():
            category_scores[category] = score
        
        # Calculate overall toxicity score (max of all category scores)
        toxicity_score = max(category_scores.values()) if category_scores else 0.0
        
        return {
            'flagged': result.flagged,
            'categories': flagged_categories,
            'toxicity_score': min(toxicity_score, 1.0),  # Ensure it's between 0-1
            'category_scores': category_scores
        }


class LocalModerator:
    """Local AI moderation using better-profanity and vaderSentiment"""
    
    def __init__(self):
        self.profanity_available = PROFANITY_AVAILABLE
        self.sentiment_available = SENTIMENT_AVAILABLE
        
        # Initialize profanity filter
        if self.profanity_available:
            profanity.load_censor_words()
            # Add custom words for Indian context
            custom_words = [
                'idiot', 'stupid', 'dumb', 'moron', 'loser',
                'hate', 'kill', 'die', 'murder', 'suicide'
            ]
            profanity.add_censor_words(custom_words)
        
        # Initialize sentiment analyzer
        if self.sentiment_available:
            self.analyzer = SentimentIntensityAnalyzer()
        
        logger.info(f"Local moderator initialized - Profanity: {self.profanity_available}, Sentiment: {self.sentiment_available}")
    
    def check_content(self, content: str) -> Dict:
        """
        Check content using local libraries
        Returns: {
            'flagged': bool,
            'categories': List[str],
            'toxicity_score': float,
            'profanity_detected': bool,
            'sentiment_scores': Dict
        }
        """
        result = {
            'flagged': False,
            'categories': [],
            'toxicity_score': 0.0,
            'profanity_detected': False,
            'sentiment_scores': {}
        }
        
        try:
            # Check for profanity
            if self.profanity_available:
                result['profanity_detected'] = profanity.contains_profanity(content)
                if result['profanity_detected']:
                    result['categories'].append('profanity')
                    result['toxicity_score'] = max(result['toxicity_score'], 0.6)
            
            # Analyze sentiment
            if self.sentiment_available:
                sentiment_scores = self.analyzer.polarity_scores(content)
                result['sentiment_scores'] = sentiment_scores
                
                # High negative sentiment indicates toxicity
                if sentiment_scores['neg'] > 0.7:
                    result['categories'].append('negative_sentiment')
                    result['toxicity_score'] = max(result['toxicity_score'], sentiment_scores['neg'])
                
                # Very low compound score also indicates toxicity
                if sentiment_scores['compound'] < -0.8:
                    result['categories'].append('very_negative')
                    result['toxicity_score'] = max(result['toxicity_score'], abs(sentiment_scores['compound']))
            
            # Check for specific harmful patterns
            harmful_patterns = self._check_harmful_patterns(content)
            if harmful_patterns:
                result['categories'].extend(harmful_patterns)
                result['toxicity_score'] = max(result['toxicity_score'], 0.8)
            
            # Set flagged status
            result['flagged'] = result['toxicity_score'] > 0.5
            
            return result
            
        except Exception as e:
            logger.error(f"Local moderation error: {e}")
            return {
                'flagged': False,
                'categories': [],
                'toxicity_score': 0.0,
                'profanity_detected': False,
                'sentiment_scores': {},
                'error': str(e)
            }
    
    def _check_harmful_patterns(self, content: str) -> List[str]:
        """Check for specific harmful patterns"""
        content_lower = content.lower()
        categories = []
        
        # Violence indicators
        violence_keywords = ['kill', 'murder', 'hurt', 'harm', 'violence', 'attack', 'fight']
        if any(keyword in content_lower for keyword in violence_keywords):
            categories.append('violence')
        
        # Self-harm indicators
        self_harm_keywords = ['suicide', 'kill myself', 'end my life', 'self harm', 'cut myself']
        if any(keyword in content_lower for keyword in self_harm_keywords):
            categories.append('self_harm')
        
        # Harassment indicators
        harassment_keywords = ['stupid', 'idiot', 'loser', 'worthless', 'pathetic']
        if any(keyword in content_lower for keyword in harassment_keywords):
            categories.append('harassment')
        
        # Spam indicators (excessive repetition)
        words = content_lower.split()
        if len(words) > 5:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
                categories.append('spam')
        
        return categories


class ModerationService:
    """Enhanced service for AI content moderation with heat system integration"""
    
    def __init__(self):
        from django.conf import settings
        self.settings = settings.MODERATION_SETTINGS
        self.enabled = self.settings.get('ENABLED', True)
        self.toxicity_threshold = self.settings.get('TOXICITY_THRESHOLD', 0.85)
        self.block_violence = self.settings.get('BLOCK_VIOLENCE', True)
        self.block_self_harm = self.settings.get('BLOCK_SELF_HARM', True)
        self.block_harassment = self.settings.get('BLOCK_HARASSMENT', False)
        
        self.openai_moderator = OpenAIModerator()
        self.local_moderator = LocalModerator()
        self.heat_system = HeatSystem()
    
    @classmethod
    def moderate_content(cls, message: Message) -> ModerationResult:
        """Moderate message content using AI with heat system integration"""
        service = cls()
        
        # Check if moderation is enabled
        if not service.enabled:
            # Moderation disabled - approve all messages
            return ModerationResult.objects.create(
                message=message,
                user=message.sender.user,
                toxicity_score=0.0,
                flagged_categories=[],
                action_taken='approved'
            )
        
        try:
            # Try OpenAI first, then fall back to local moderation
            moderation_result = service._get_moderation_result(message.content)
            
            # Determine action based on results
            action = service._determine_action(moderation_result)
            
            # Handle violations if content is flagged
            if action in ['rejected', 'shadowban']:
                service._handle_violation(
                    message.sender.user, 
                    moderation_result['toxicity_score'], 
                    message.content,
                    moderation_result['categories']
                )
            
            # Create moderation result record
            result = ModerationResult.objects.create(
                message=message,
                user=message.sender.user,
                toxicity_score=moderation_result['toxicity_score'],
                flagged_categories=moderation_result['categories'],
                action_taken=action
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error moderating message {message.id}: {e}")
            # Default to approved if moderation fails
            return ModerationResult.objects.create(
                message=message,
                user=message.sender.user,
                toxicity_score=0.0,
                flagged_categories=[],
                action_taken='approved'
            )
    
    def _get_moderation_result(self, content: str) -> Dict:
        """Get moderation result with fallback logic"""
        # Try OpenAI first
        if self.openai_moderator.available:
            openai_result = self.openai_moderator.check_content(content)
            if 'error' not in openai_result:
                logger.info("Using OpenAI moderation result")
                return openai_result
            else:
                logger.warning(f"OpenAI moderation failed: {openai_result.get('error')}")
        
        # Fall back to local moderation
        logger.info("Using local moderation as fallback")
        local_result = self.local_moderator.check_content(content)
        return local_result
    
    def _determine_action(self, moderation_result: Dict) -> str:
        """Determine action based on moderation result and settings"""
        toxicity_score = moderation_result.get('toxicity_score', 0.0)
        categories = moderation_result.get('categories', [])
        
        # Check if specific categories should be blocked based on settings
        if self.block_violence and 'violence' in categories:
            return 'rejected'
        
        if self.block_self_harm and 'self_harm' in categories:
            return 'rejected'
        
        if self.block_harassment and 'harassment' in categories and toxicity_score >= self.toxicity_threshold:
            return 'shadowban'
        
        # Warning for moderate violations (but allow message through)
        if toxicity_score >= self.toxicity_threshold:
            return 'warning'
        
        # Approve if below threshold
        return 'approved'
    
    def _handle_violation(self, user: User, toxicity_score: float, content: str, categories: List[str]):
        """Handle content violation with heat system integration"""
        # Determine violation type based on categories
        violation_type = 'toxicity'  # default
        if 'violence' in categories:
            violation_type = 'violence'
        elif 'self_harm' in categories:
            violation_type = 'self_harm'
        elif 'harassment' in categories:
            violation_type = 'harassment'
        elif 'spam' in categories:
            violation_type = 'spam'
        
        # Create violation record
        violation = ViolationHistory.objects.create(
            user=user,
            violation_type=violation_type,
            toxicity_score=toxicity_score,
            content_snippet=content[:200],
            action_taken='shadowban'
        )
        
        # Apply heat-based penalties
        base_duration = 24  # 24 hours base
        duration_hours = self.heat_system.apply_heat_penalty(user, base_duration, toxicity_score)
        
        self._apply_shadowban(user, duration_hours, f"Content violation: {violation_type} (score: {toxicity_score})")
        
        # Deduct reputation points
        try:
            from reputation.services import ReputationService
            ReputationService.award_points(user, 'validated_report')
        except ImportError:
            logger.warning("Reputation service not available")
        
        # Log heat system info
        heat_info = self.heat_system.get_heat_info(user)
        logger.info(f"User {user.id} heat level: {heat_info['heat_level']} ({heat_info['heat_name']})")
        
        # Broadcast real-time moderation notification
        self._broadcast_moderation_notification(user, violation_type, toxicity_score, duration_hours)
    
    def _broadcast_moderation_notification(self, user: User, violation_type: str, toxicity_score: float, duration_hours: int):
        """Broadcast moderation notification via WebSocket"""
        try:
            from reputation.websocket_utils import realtime_notifier
            
            # Send notification to the user
            realtime_notifier.broadcast_moderation_notification(
                user_id=user.id,
                notification_type='content_rejected',
                message=f'Your content was rejected for {violation_type}',
                details={
                    'violation_type': violation_type,
                    'toxicity_score': toxicity_score,
                    'shadowban_duration': duration_hours,
                    'reason': f'Content violated community guidelines: {violation_type}'
                }
            )
        except ImportError:
            # WebSocket utilities not available, skip broadcasting
            pass
    
    @classmethod
    def _apply_shadowban(cls, user: User, duration_hours: int, reason: str):
        """Apply shadowban to user"""
        # Check for existing active shadowban
        existing_ban = Shadowban.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        
        if existing_ban:
            # Extend existing shadowban
            existing_ban.expires_at += timedelta(hours=duration_hours)
            existing_ban.save()
            logger.info(f"Extended shadowban for user {user.id} by {duration_hours} hours")
        else:
            # Create new shadowban
            Shadowban.objects.create(
                user=user,
                reason=reason,
                duration_hours=duration_hours
            )
            logger.info(f"Applied {duration_hours}h shadowban to user {user.id}")
        
        # Broadcast shadowban notification
        cls._broadcast_shadowban_notification(user, duration_hours, reason)
    
    @classmethod
    def _broadcast_shadowban_notification(cls, user: User, duration_hours: int, reason: str):
        """Broadcast shadowban notification via WebSocket"""
        try:
            from reputation.websocket_utils import realtime_notifier
            
            realtime_notifier.broadcast_moderation_notification(
                user_id=user.id,
                notification_type='user_shadowbanned',
                message=f'You have been temporarily restricted for {duration_hours} hours',
                details={
                    'duration_hours': duration_hours,
                    'reason': reason,
                    'expires_at': (timezone.now() + timedelta(hours=duration_hours)).isoformat()
                }
            )
        except ImportError:
            # WebSocket utilities not available, skip broadcasting
            pass
    
    @classmethod
    def is_user_shadowbanned(cls, user: User) -> bool:
        """Check if user is currently shadowbanned"""
        return Shadowban.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).exists()
    
    @classmethod
    def get_user_heat_level(cls, user: User) -> int:
        """Get user's current heat level (delegated to HeatSystem)"""
        return HeatSystem.get_user_heat_level(user)
    
    @classmethod
    def get_user_heat_info(cls, user: User) -> Dict:
        """Get comprehensive heat information for user"""
        return HeatSystem.get_heat_info(user)
    
    @classmethod
    def attempt_user_rehabilitation(cls, user: User) -> bool:
        """Attempt to rehabilitate user by reducing heat level"""
        return HeatSystem.attempt_rehabilitation(user)