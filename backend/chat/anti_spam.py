"""
Advanced Anti-Spam Protection System
Implements multiple layers of spam detection and prevention
"""
import time
import hashlib
from typing import Dict, List, Tuple, Optional
from django.core.cache import cache
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AntiSpamSystem:
    """
    Multi-layered spam protection system with smart detection
    Designed to catch real spam while allowing natural conversation
    """
    
    # Configuration
    MESSAGE_RATE_LIMIT = 15  # messages per window 
    MESSAGE_RATE_WINDOW = 10  # seconds
    
    TYPING_RATE_LIMIT = 30  # typing events per window 
    TYPING_RATE_WINDOW = 10  # seconds
    
    DUPLICATE_MESSAGE_WINDOW = 60  # seconds to check for duplicates
    MAX_DUPLICATE_MESSAGES = 3  # max same message in window 
    
    SIMILARITY_THRESHOLD = 0.92  # 92% similarity = spam
    SIMILARITY_CHECK_COUNT = 5  # check last N messages
    MIN_MESSAGE_LENGTH_FOR_SIMILARITY = 15  # Don't check similarity for short messages
    
    BURST_THRESHOLD = 7  # messages in burst window (increased for rapid conversation)
    BURST_WINDOW = 3  # seconds (increased window)
    
    # Short message exemptions (common in natural chat)
    SHORT_MESSAGE_THRESHOLD = 10  # characters
    SHORT_MESSAGE_BURST_MULTIPLIER = 1.5  # Allow more bursts for short messages
    
    ESCALATION_THRESHOLDS = {
        'warning': 5,  # violations before warning 
        'temp_mute': 8,  # violations before temp mute 
        'shadowban': 15,  # violations before shadowban
    }
    
    TEMP_MUTE_DURATION = 180  # 3 minutes 
    
    def __init__(self, user_id: int, chatroom_id: str):
        self.user_id = user_id
        self.chatroom_id = chatroom_id
        self.cache_prefix = f'antispam:{user_id}:{chatroom_id}'
    
    # ==================== Rate Limiting ====================
    
    async def check_message_rate_limit(self) -> Tuple[bool, Optional[str]]:
        """
        Check if user is within message rate limits
        Returns: (is_allowed, error_message)
        """
        cache_key = f'{self.cache_prefix}:msg_rate'
        
        # Get current count
        count = await self._cache_get(cache_key, 0)
        
        if count >= self.MESSAGE_RATE_LIMIT:
            # Check if user is a repeat offender
            await self._record_violation('rate_limit')
            return False, f'Rate limit exceeded. Please wait {self.MESSAGE_RATE_WINDOW} seconds.'
        
        # Increment counter
        await self._cache_incr(cache_key, self.MESSAGE_RATE_WINDOW)
        return True, None
    
    async def check_typing_rate_limit(self) -> bool:
        """Check typing indicator rate limit"""
        cache_key = f'{self.cache_prefix}:typing_rate'
        count = await self._cache_get(cache_key, 0)
        
        if count >= self.TYPING_RATE_LIMIT:
            return False
        
        await self._cache_incr(cache_key, self.TYPING_RATE_WINDOW)
        return True
    
    # ==================== Duplicate Detection ====================
    
    async def check_duplicate_message(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check if message is a duplicate with smart exemptions
        Returns: (is_allowed, error_message)
        """
        # Exempt very short messages (like "ok", "yes", "lol", "hi")
        if len(content.strip()) <= 5:
            return True, None
        
        # Exempt common short responses
        common_responses = ['ok', 'okay', 'yes', 'no', 'yeah', 'nope', 'lol', 'lmao', 
                           'haha', 'hehe', 'hi', 'hey', 'bye', 'thanks', 'thank you',
                           'welcome', 'sure', 'cool', 'nice', 'great', 'good', 'bad']
        if content.lower().strip() in common_responses:
            return True, None
        
        # Create hash of message content
        content_hash = self._hash_content(content)
        cache_key = f'{self.cache_prefix}:duplicates'
        
        # Get recent message hashes with timestamps
        recent_hashes = await self._cache_get(cache_key, [])
        current_time = time.time()
        
        # Filter out old entries
        recent_hashes = [h for h in recent_hashes if current_time - h['time'] < self.DUPLICATE_MESSAGE_WINDOW]
        
        # Count duplicates
        duplicate_count = sum(1 for h in recent_hashes if h['hash'] == content_hash)
        
        if duplicate_count >= self.MAX_DUPLICATE_MESSAGES:
            await self._record_violation('duplicate_spam')
            return False, 'Duplicate message detected. Please send different content.'
        
        # Add to recent hashes with timestamp
        recent_hashes.append({'hash': content_hash, 'time': current_time})
        # Keep only recent hashes (last 15)
        recent_hashes = recent_hashes[-15:]
        
        await self._cache_set(cache_key, recent_hashes, self.DUPLICATE_MESSAGE_WINDOW)
        return True, None
    
    # ==================== Similarity Detection ====================
    
    async def check_message_similarity(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check if message is too similar to recent messages with smart exemptions
        Returns: (is_allowed, error_message)
        """
        # Skip similarity check for short messages (natural chat has many short similar messages)
        if len(content.strip()) < self.MIN_MESSAGE_LENGTH_FOR_SIMILARITY:
            return True, None
        
        # Skip for common conversational patterns
        if self._is_conversational_pattern(content):
            return True, None
        
        cache_key = f'{self.cache_prefix}:recent_messages'
        recent_messages = await self._cache_get(cache_key, [])
        
        # Check similarity with recent messages
        similar_count = 0
        for recent_msg in recent_messages[-self.SIMILARITY_CHECK_COUNT:]:
            # Skip if recent message is also short
            if len(recent_msg.strip()) < self.MIN_MESSAGE_LENGTH_FOR_SIMILARITY:
                continue
                
            similarity = self._calculate_similarity(content, recent_msg)
            if similarity >= self.SIMILARITY_THRESHOLD:
                similar_count += 1
        
        # Only flag if multiple similar messages (not just one)
        if similar_count >= 2:
            await self._record_violation('similar_spam')
            return False, 'Message too similar to recent messages. Please vary your content.'
        
        # Add to recent messages
        recent_messages.append(content)
        recent_messages = recent_messages[-self.SIMILARITY_CHECK_COUNT:]
        
        await self._cache_set(cache_key, recent_messages, 60)
        return True, None
    
    # ==================== Burst Detection ====================
    
    async def check_burst_spam(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Detect rapid-fire message bursts with smart exemptions
        Returns: (is_allowed, error_message)
        """
        cache_key = f'{self.cache_prefix}:burst'
        timestamps = await self._cache_get(cache_key, [])
        
        current_time = time.time()
        
        # Remove old timestamps
        timestamps = [ts for ts in timestamps if current_time - ts < self.BURST_WINDOW]
        
        # Adjust threshold for short messages (natural rapid chat)
        is_short = len(content.strip()) < self.SHORT_MESSAGE_THRESHOLD
        threshold = self.BURST_THRESHOLD
        if is_short:
            threshold = int(self.BURST_THRESHOLD * self.SHORT_MESSAGE_BURST_MULTIPLIER)
        
        if len(timestamps) >= threshold:
            await self._record_violation('burst_spam')
            return False, 'Sending messages too quickly. Please slow down.'
        
        # Add current timestamp
        timestamps.append(current_time)
        await self._cache_set(cache_key, timestamps, self.BURST_WINDOW)
        
        return True, None
    
    # ==================== Pattern Detection ====================
    
    async def check_spam_patterns(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Detect common spam patterns with smart exemptions
        Returns: (is_allowed, error_message)
        """
        content_lower = content.lower()
        
        # Check for excessive repetition (but allow natural patterns like "hahaha", "yesss")
        if self._has_excessive_repetition(content):
            await self._record_violation('repetition_spam')
            return False, 'Excessive character repetition detected.'
        
        # Check for excessive caps (but be lenient for short messages and excitement)
        if self._has_excessive_caps(content):
            await self._record_violation('caps_spam')
            return False, 'Excessive capital letters detected.'
        
        # Check for spam keywords (commercial spam only)
        spam_keywords = [
            'click here', 'buy now', 'limited offer', 'act now', 'free money',
            'make money fast', 'work from home', 'earn $$$', 'get rich',
            'weight loss', 'viagra', 'casino', 'lottery winner'
        ]
        if any(keyword in content_lower for keyword in spam_keywords):
            await self._record_violation('keyword_spam')
            return False, 'Spam keywords detected.'
        
        # Check for excessive emojis (but be more lenient)
        emoji_count = sum(1 for char in content if ord(char) > 127000)
        if emoji_count > 15 and len(content) < 50:  # Only flag if message is mostly emojis
            await self._record_violation('emoji_spam')
            return False, 'Too many emojis in message.'
        
        # Check for URL spam (multiple URLs in short message)
        url_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org']
        url_count = sum(1 for pattern in url_patterns if pattern in content_lower)
        if url_count >= 3:  # Multiple URLs = likely spam
            await self._record_violation('url_spam')
            return False, 'Too many URLs in message.'
        
        return True, None
    
    # ==================== Mute/Ban System ====================
    
    async def is_user_muted(self) -> Tuple[bool, Optional[int]]:
        """
        Check if user is temporarily muted
        Returns: (is_muted, seconds_remaining)
        """
        cache_key = f'{self.cache_prefix}:muted'
        mute_until = await self._cache_get(cache_key)
        
        if mute_until:
            remaining = int(mute_until - time.time())
            if remaining > 0:
                return True, remaining
            else:
                # Mute expired
                await self._cache_delete(cache_key)
        
        return False, None
    
    async def apply_temp_mute(self, duration: int = None):
        """Apply temporary mute to user"""
        if duration is None:
            duration = self.TEMP_MUTE_DURATION
        
        cache_key = f'{self.cache_prefix}:muted'
        mute_until = time.time() + duration
        await self._cache_set(cache_key, mute_until, duration)
        
        logger.warning(f"User {self.user_id} temporarily muted for {duration}s in chatroom {self.chatroom_id}")
    
    # ==================== Violation Tracking ====================
    
    async def _record_violation(self, violation_type: str):
        """Record spam violation and apply escalating penalties"""
        cache_key = f'{self.cache_prefix}:violations'
        violations = await self._cache_get(cache_key, [])
        
        # Add violation with timestamp
        violations.append({
            'type': violation_type,
            'timestamp': time.time()
        })
        
        # Keep violations from last hour
        one_hour_ago = time.time() - 3600
        violations = [v for v in violations if v['timestamp'] > one_hour_ago]
        
        await self._cache_set(cache_key, violations, 3600)
        
        # Apply escalating penalties
        violation_count = len(violations)
        
        if violation_count >= self.ESCALATION_THRESHOLDS['shadowban']:
            # Trigger shadowban (handled by moderation system)
            logger.error(f"User {self.user_id} triggered shadowban threshold")
            await self._trigger_shadowban()
        elif violation_count >= self.ESCALATION_THRESHOLDS['temp_mute']:
            # Apply temp mute
            await self.apply_temp_mute()
        elif violation_count >= self.ESCALATION_THRESHOLDS['warning']:
            # Send warning
            logger.warning(f"User {self.user_id} received spam warning")
    
    async def _trigger_shadowban(self):
        """Trigger shadowban through moderation system"""
        try:
            from moderation.services import ModerationService
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            user = await self._get_user()
            
            if user:
                # Create violation record
                from moderation.models import ViolationHistory
                await self._create_violation_record(user)
        except Exception as e:
            logger.error(f"Failed to trigger shadowban: {e}")
    
    # ==================== Helper Methods ====================
    
    def _hash_content(self, content: str) -> str:
        """Create hash of message content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using Levenshtein distance
        Returns: similarity score (0.0 to 1.0)
        """
        # Simple character-based similarity
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if text1 == text2:
            return 1.0
        
        # Calculate Levenshtein distance
        len1, len2 = len(text1), len(text2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Create distance matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if text1[i-1] == text2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        similarity = 1 - (distance / max_len)
        
        return similarity
    
    def _has_excessive_repetition(self, content: str) -> bool:
        """
        Check for excessive character repetition
        Allows natural patterns like "hahaha", "yesss", "noooo"
        """
        if len(content) < 3:
            return False
        
        # Allow common natural repetitions
        natural_patterns = ['haha', 'hehe', 'lol', 'lmao', 'omg', 'wow', 'yes', 'no', 'ok']
        content_lower = content.lower()
        for pattern in natural_patterns:
            if pattern * 2 in content_lower or pattern * 3 in content_lower:
                return False  # Allow "hahaha", "lolol", etc.
        
        # Check for excessive single character repetition (e.g., "aaaaaaaaaa")
        # But allow up to 5 repetitions for emphasis (e.g., "yesss", "noooo")
        for i in range(len(content) - 6):
            if all(content[i] == content[i+j] for j in range(7)):
                return True  # 7+ same characters in a row = spam
        
        # Check for repeated patterns longer than natural (e.g., "abcabcabcabc")
        for pattern_len in [3, 4, 5]:
            for i in range(len(content) - pattern_len * 4):
                pattern = content[i:i+pattern_len]
                if content[i:i+pattern_len*4] == pattern * 4:
                    # But allow if it's a natural pattern
                    if pattern.lower() not in ['ha', 'he', 'lo', 'la']:
                        return True
        
        return False
    
    def _has_excessive_caps(self, content: str) -> bool:
        """
        Check for excessive capital letters
        More lenient for short messages and allows emphasis
        """
        # Don't check very short messages
        if len(content) < 15:
            return False
        
        # Count only letters (ignore numbers, punctuation)
        letters = [c for c in content if c.isalpha()]
        if len(letters) < 10:
            return False
        
        caps_count = sum(1 for c in letters if c.isupper())
        caps_ratio = caps_count / len(letters)
        
        # More lenient threshold - 80% caps (was 70%)
        return caps_ratio > 0.80
    
    def _is_conversational_pattern(self, content: str) -> bool:
        """
        Check if message follows common conversational patterns
        These should be exempt from similarity checks
        """
        content_lower = content.lower().strip()
        
        # Question patterns
        if content_lower.endswith('?'):
            return True
        
        # Greeting patterns
        greetings = ['hi', 'hello', 'hey', 'sup', 'yo', 'morning', 'evening', 'night']
        if any(content_lower.startswith(g) for g in greetings):
            return True
        
        # Agreement/disagreement patterns
        agreements = ['i agree', 'i think', 'i feel', 'i know', 'i see', 'makes sense',
                     'you\'re right', 'that\'s true', 'exactly', 'totally']
        if any(phrase in content_lower for phrase in agreements):
            return True
        
        # Reaction patterns
        reactions = ['lol', 'lmao', 'haha', 'omg', 'wow', 'nice', 'cool', 'awesome']
        if any(reaction in content_lower for reaction in reactions):
            return True
        
        return False
    
    # ==================== Cache Operations ====================
    
    async def _cache_get(self, key: str, default=None):
        """Async cache get"""
        from asgiref.sync import sync_to_async
        return await sync_to_async(cache.get)(key, default)
    
    async def _cache_set(self, key: str, value, timeout: int):
        """Async cache set"""
        from asgiref.sync import sync_to_async
        return await sync_to_async(cache.set)(key, value, timeout)
    
    async def _cache_incr(self, key: str, timeout: int):
        """Async cache increment"""
        from asgiref.sync import sync_to_async
        try:
            return await sync_to_async(cache.incr)(key)
        except ValueError:
            # Key doesn't exist, create it
            await sync_to_async(cache.set)(key, 1, timeout)
            return 1
    
    async def _cache_delete(self, key: str):
        """Async cache delete"""
        from asgiref.sync import sync_to_async
        return await sync_to_async(cache.delete)(key)
    
    async def _get_user(self):
        """Get user object"""
        from asgiref.sync import sync_to_async
        try:
            return await sync_to_async(User.objects.get)(id=self.user_id)
        except User.DoesNotExist:
            return None
    
    async def _create_violation_record(self, user):
        """Create violation record in database"""
        from asgiref.sync import sync_to_async
        from moderation.models import ViolationHistory
        
        await sync_to_async(ViolationHistory.objects.create)(
            user=user,
            violation_type='spam',
            toxicity_score=0.9,
            content_snippet='Automated spam detection',
            action_taken='shadowban'
        )


class SpamDetectionMiddleware:
    """
    Middleware to apply spam detection to all WebSocket messages
    """
    
    @staticmethod
    async def check_all(user_id: int, chatroom_id: str, content: str, event_type: str) -> Tuple[bool, Optional[str]]:
        """
        Run all spam checks with smart detection
        Returns: (is_allowed, error_message)
        """
        spam_detector = AntiSpamSystem(user_id, chatroom_id)
        
        # Check if user is muted
        is_muted, remaining = await spam_detector.is_user_muted()
        if is_muted:
            return False, f'You are temporarily muted. Please wait {remaining} seconds.'
        
        # For message sends, run all checks
        if event_type == 'message.send':
            # Rate limit check
            allowed, error = await spam_detector.check_message_rate_limit()
            if not allowed:
                return False, error
            
            # Burst detection (with content for smart detection)
            allowed, error = await spam_detector.check_burst_spam(content)
            if not allowed:
                return False, error
            
            # Duplicate detection (with smart exemptions)
            allowed, error = await spam_detector.check_duplicate_message(content)
            if not allowed:
                return False, error
            
            # Similarity detection (with smart exemptions)
            allowed, error = await spam_detector.check_message_similarity(content)
            if not allowed:
                return False, error
            
            # Pattern detection (with smart exemptions)
            allowed, error = await spam_detector.check_spam_patterns(content)
            if not allowed:
                return False, error
        
        # For typing indicators, just check rate limit
        elif event_type == 'typing.start':
            allowed = await spam_detector.check_typing_rate_limit()
            if not allowed:
                return False, 'Typing indicator rate limit exceeded.'
        
        return True, None
