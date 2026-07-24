"""
Advanced Anti-Spam Protection System
Implements multiple layers of spam detection and prevention
"""
import time
import hashlib
import logging
import difflib
from typing import Dict, List, Tuple, Optional

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class AntiSpamSystem:
    """
    Multi-layered spam protection system with smart detection
    Designed to catch real spam while allowing natural conversation
    """
    
    # config
    MESSAGE_RATE_LIMIT = 15 
    MESSAGE_RATE_WINDOW = 10 
    
    TYPING_RATE_LIMIT = 30  
    TYPING_RATE_WINDOW = 10  
    
    DUPLICATE_MESSAGE_WINDOW = 60 
    MAX_DUPLICATE_MESSAGES = 3 
    
    SIMILARITY_THRESHOLD = 0.92 
    SIMILARITY_CHECK_COUNT = 5 
    MIN_MESSAGE_LENGTH_FOR_SIMILARITY = 15  
    MAX_MESSAGE_LENGTH_FOR_SIMILARITY = 1000

    BURST_THRESHOLD = 7 
    BURST_WINDOW = 3 
    
    # Short msg exemptions 
    SHORT_MESSAGE_THRESHOLD = 10 
    SHORT_MESSAGE_BURST_MULTIPLIER = 1.5 
    
    ESCALATION_THRESHOLDS = {
        'warning': 5,  
        'temp_mute': 8,  
        'shadowban': 15,  
    }
    
    TEMP_MUTE_DURATION = 180  
    
    def __init__(self, user_id: int, chatroom_id: str):
        self.user_id = user_id
        self.chatroom_id = chatroom_id
        self.cache_prefix = f'antispam:{user_id}:{chatroom_id}'
    
    #  rate limiting
    
    async def check_message_rate_limit(self) -> Tuple[bool, Optional[str]]:
        cache_key = f'{self.cache_prefix}:msg_rate'
        
        # INCR is atomic , no race possible better than get then incr
        new_count = await self._cache_incr(cache_key, self.MESSAGE_RATE_WINDOW)
        
        if new_count > self.MESSAGE_RATE_LIMIT:
            if(new_count == self.MESSAGE_RATE_LIMIT +1):
                await self._record_violation('rate_limit')
            return False, f'Rate limit exceeded. Please wait {self.MESSAGE_RATE_WINDOW} seconds.'
        
        return True, None

    
    async def check_typing_rate_limit(self) -> bool:
        """Check typing indicator rate limit"""
        cache_key = f'{self.cache_prefix}:typing_rate'
        count = await self._cache_incr(cache_key, self.TYPING_RATE_WINDOW)
        
        return count<= self.TYPING_RATE_LIMIT 
    
    # duplicate detection
    
    async def check_duplicate_message(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check if message is a duplicate with smart exemptions
        Returns: (is_allowed, error_message)
        """
        
        if len(content.strip()) <= 5:
            return True, None
        
        common_responses = ['ok', 'okay', 'yes', 'no', 'yeah', 'nope', 'lol', 'lmao', 
                           'haha', 'hehe', 'hi', 'hey', 'bye', 'thanks', 'thank you',
                           'welcome', 'sure', 'cool', 'nice', 'great', 'good', 'bad']
        if content.lower().strip() in common_responses:
            return True, None
        
        content_hash = self._hash_content(content)
        cache_key = f'{self.cache_prefix}:duplicates'
        
        # Get recent message hashes with timestamps
        recent_hashes = await self._cache_get(cache_key, [])
        current_time = time.time()
        
        recent_hashes = [h for h in recent_hashes if current_time - h['time'] < self.DUPLICATE_MESSAGE_WINDOW]
        
        duplicate_count = sum(1 for h in recent_hashes if h['hash'] == content_hash)
        
        if duplicate_count >= self.MAX_DUPLICATE_MESSAGES:
            await self._record_violation('duplicate_spam')
            return False, 'Duplicate message detected. dont spam same content.'
        
        # Add to recent hashes with timestamp
        recent_hashes.append({'hash': content_hash, 'time': current_time})
        recent_hashes = recent_hashes[-15:]
        
        await self._cache_set(cache_key, recent_hashes, self.DUPLICATE_MESSAGE_WINDOW)
        return True, None
    
    # similarity detection
    
    async def check_message_similarity(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check if message is too similar to recent messages with smart exemptions
        Returns: (is_allowed, error_message)
        """
        l = len(content.strip())
        if l < self.MIN_MESSAGE_LENGTH_FOR_SIMILARITY or l > self.MAX_MESSAGE_LENGTH_FOR_SIMILARITY:
            return True, None
        
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
        
        # Only flag if multiple similar messages 
        if similar_count >= 2:
            await self._record_violation('similar_spam')
            return False, 'Message too similar to recent messages. Please vary your content.'
        
       
        recent_messages.append(content)
        recent_messages = recent_messages[-self.SIMILARITY_CHECK_COUNT:]
        
        await self._cache_set(cache_key, recent_messages, 60)
        return True, None
    
    # burst detection
    
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
        
        # Adjust threshold for short messages 
        is_short = len(content.strip()) < self.SHORT_MESSAGE_THRESHOLD
        threshold = self.BURST_THRESHOLD
        if is_short:
            threshold = int(self.BURST_THRESHOLD * self.SHORT_MESSAGE_BURST_MULTIPLIER)
        
        if len(timestamps) >= threshold:
            await self._record_violation('burst_spam')
            return False, 'slow down kid.'
        
       
        timestamps.append(current_time)
        await self._cache_set(cache_key, timestamps, self.BURST_WINDOW)
        
        return True, None
    
    # pattern detection
    
    async def check_spam_patterns(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Detect common spam patterns with smart exemptions
        Returns: (is_allowed, error_message)
        """
        # content_lower = content.lower()
        
        # Check for excessive repetition (but allow natural patterns like "hahaha", "yesss")
        # if self._has_excessive_repetition(content):
        #     await self._record_violation('repetition_spam')
        #     return False, 'Excessive character repetition detected.'
        
        # if self._has_excessive_caps(content):
        #     await self._record_violation('caps_spam')
        #     return False, 'Excessive capital letters detected.'
        
        
        # spam_keywords = [
        #     'click here', 'buy now', 'limited offer', 'act now', 'free money',
        #     'make money fast', 'earn $$$', 'get rich',  'get this course'
        # ]
        # if any(keyword in content_lower for keyword in spam_keywords):
        #     await self._record_violation('keyword_spam')
        #     return False, 'Spam keywords detected.'
        
        # Check for excessive emojis 
        # emoji_count = sum(1 for char in content if ord(char) > 127000)
        # if emoji_count > 15 and len(content) < 50:  
        #     await self._record_violation('emoji_spam')
        #     return False, 'Too many emojis in message.'
        
        # Check for URL spam (multiple URLs in short message)
        # url_patterns = ['http://', 'https://', 'www.', '.com', '.net', '.org']
        # url_count = sum(1 for pattern in url_patterns if pattern in content_lower)
        # if url_count >= 3:  # Multiple URLs = likely spam
        #     await self._record_violation('url_spam')
        #     return False, 'Too many URLs in message.'
        
        return True, None
    
    # Mute-nan System 
    
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
    
    # Violation Tracking
    
    async def _record_violation(self, violation_type: str):
        """Record spam violation and apply escalating penalties"""
        cache_key = f'{self.cache_prefix}:violations'
        violations = await self._cache_get(cache_key, [])
        
        curr_time = time.time()
        violations.append({
            'type': violation_type,
            'timestamp': curr_time
        })
         
        violations = [v for v in violations if v['timestamp'] > curr_time - 3600]
        
        await self._cache_set(cache_key, violations, 3600)
        
        
        violation_count = len(violations)
        
        if violation_count >= self.ESCALATION_THRESHOLDS['shadowban']:
            
            logger.error(f"User {self.user_id} triggered shadowban threshold")
            await self._trigger_shadowban()
        elif violation_count >= self.ESCALATION_THRESHOLDS['temp_mute']:
            
            await self.apply_temp_mute()
        elif violation_count >= self.ESCALATION_THRESHOLDS['warning']:
            
            logger.warning(f"User {self.user_id} received spam warning")
    
    async def _trigger_shadowban(self):
        """Trigger shadowban through moderation system"""
        try:
            from moderation.services import ModerationService
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            user = await self._get_user()
            
            if user:
                from moderation.models import ViolationHistory
                await self._create_violation_record(user)
        except Exception as e:
            logger.error(f"Failed to trigger shadowban: {e}")
    
    #  Helper Methods 
    
    def _hash_content(self, content: str) -> str:
        """Create hash of message content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using Levenshtein distance
        Returns: similarity score (0.0 to 1.0)
        """
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if text1 == text2:
            return 1.0
        
        # cal levenshtein dist
        len1, len2 = len(text1), len(text2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        #  dist matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if text1[i-1] == text2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # del
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # sub
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
        
        natural_patterns = ['haha', 'hehe', 'lol', 'lmao', 'omg', 'wow', 'yes', 'no', 'ok']
        content_lower = content.lower()
        for pattern in natural_patterns:
            if pattern * 2 in content_lower or pattern * 3 in content_lower:
                return False 
        
        for i in range(len(content) - 6):
            if all(content[i] == content[i+j] for j in range(7)):
                return True  
        
        for pattern_len in [3, 4, 5]:
            for i in range(len(content) - pattern_len * 4):
                pattern = content[i:i+pattern_len]
                if content[i:i+pattern_len*4] == pattern * 4:
                    if pattern.lower() not in ['ha', 'he', 'lo', 'la']:
                        return True
        
        return False
    
    def _has_excessive_caps(self, content: str) -> bool:
        """
        Check for excessive capital letters
        More lenient for short messages and allows emphasis
        """
        # if len(content) < 15:
        #     return False
        
        # letters = [c for c in content if c.isalpha()]
        # if len(letters) < 10:
        #     return False
        
        # caps_count = sum(1 for c in letters if c.isupper())
        # caps_ratio = caps_count / len(letters)
        
        # return caps_ratio > 0.80

        return false
    
    def _is_conversational_pattern(self, content: str) -> bool:
        """
        Check if message follows common conversational patterns
        These should be exempt from similarity checks
        """
        content_lower = content.lower().strip()
        
        if content_lower.endswith('?'):
            return True
        
        greetings = ['hi', 'hello', 'hey', 'sup', 'yo', 'morning', 'evening', 'night']
        if any(content_lower.startswith(g) for g in greetings):
            return True
        
        # Agreement and disagreement patterns
        agreements = ['i agree', 'i think', 'i feel', 'i know', 'i see', 'makes sense',
                     'you\'re right', 'that\'s true', 'exactly', 'totally']
        if any(phrase in content_lower for phrase in agreements):
            return True
        
        # Reaction 
        reactions = ['lol', 'lmao', 'haha', 'omg', 'wow', 'nice', 'cool', 'awesome']
        if any(reaction in content_lower for reaction in reactions):
            return True
        
        return False
    
    # Cache ops
    
    async def _cache_get(self, key: str, default=None):
        """Async cache get"""
        return await sync_to_async(cache.get)(key, default)
    
    async def _cache_set(self, key: str, value, timeout: int):
        """Async cache set"""
        return await sync_to_async(cache.set)(key, value, timeout)
    
    async def _cache_incr(self, key: str, timeout: int):
        """Async cache increment"""
        try:
            return await sync_to_async(cache.incr)(key)
        except ValueError:
            
            await sync_to_async(cache.set)(key, 1, timeout)
            return 1
    
    async def _cache_delete(self, key: str):
        """Async cache delete"""
        return await sync_to_async(cache.delete)(key)
    
    async def _get_user(self):
        """Get user object"""
        try:
            return await sync_to_async(User.objects.get)(id=self.user_id)
        except User.DoesNotExist:
            return None
    
    async def _create_violation_record(self, user):
        """Create violation record in database"""
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
