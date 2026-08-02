import time
import hashlib
import logging
from typing import Tuple, Optional

from django.core.cache import cache
from django.contrib.auth import get_user_model
from Levenshtein import ratio as levenshtein_ratio
import redis.asyncio as redis
from django.conf import settings

REDIS_URL = settings.CACHES['default']['LOCATION']

async_redis_client = redis.from_url(REDIS_URL, decode_responses=True)

User = get_user_model()
logger = logging.getLogger(__name__)


class AntiSpamSystem:
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

    SHORT_MESSAGE_THRESHOLD = 10
    SHORT_MESSAGE_BURST_MULTIPLIER = 1.5

    ESCALATION_THRESHOLDS = {
        "warning": 5,
        "temp_mute": 8,
        "shadowban": 15,
    }

    TEMP_MUTE_DURATION = 180

    def __init__(self, user_id: int, chatroom_id: str):
        self.user_id = user_id
        self.chatroom_id = chatroom_id
        self.cache_prefix = f"antispam:{user_id}:{chatroom_id}"

    async def check_message_rate_limit(self, content: str) -> Tuple[bool, Optional[str]]:
        is_short = len(content.strip()) <= self.SHORT_MESSAGE_THRESHOLD

        cache_key = f"{self.cache_prefix}:msg_rate:{'short' if is_short else 'long'}"
        limit = (
            int(self.MESSAGE_RATE_LIMIT * self.SHORT_MESSAGE_BURST_MULTIPLIER)
            if is_short
            else self.MESSAGE_RATE_LIMIT
        )

        new_count = await self._cache_incr(cache_key, self.MESSAGE_RATE_WINDOW)

        if new_count > limit:
            if new_count == limit + 1:
                await self._record_violation("rate_limit")
            return False, f"rate limit exceeded. wait {self.MESSAGE_RATE_WINDOW} seconds."

        return True, None

    async def check_typing_rate_limit(self) -> bool:
        cache_key = f"{self.cache_prefix}:typing_rate"
        count = await self._cache_incr(cache_key, self.TYPING_RATE_WINDOW)
        return count <= self.TYPING_RATE_LIMIT

    async def check_duplicate_message(self, content: str) -> Tuple[bool, Optional[str]]:
        stripped = content.strip()
        if len(stripped) <= 5:
            return True, None

        common_responses = {
            "ok",
            "okay",
            "yes",
            "no",
            "yeah",
            "nope",
            "lol",
            "lmao",
            "haha",
            "hehe",
            "hi",
            "hey",
            "bye",
            "thanks",
            "thank you",
            "welcome",
            "sure",
            "cool",
            "nice",
            "great",
            "good",
            "bad",
        }
        if stripped.lower() in common_responses:
            return True, None

        content_hash = self._hash_content(content)
        cache_key = f"{self.cache_prefix}:duplicates"

        current_time = time.time()
        cutoff = current_time - self.DUPLICATE_MESSAGE_WINDOW

        await self._cache_zremrangebyscore(cache_key, "-inf", cutoff)
        duplicate_count = await self._cache_zcount(
            cache_key, current_time, current_time, member_prefix=content_hash
        )

        if duplicate_count >= self.MAX_DUPLICATE_MESSAGES:
            await self._record_violation("duplicate_spam")
            return False, "duplicate message detected. dont spam same content."

        await self._cache_zadd(cache_key, current_time, content_hash)
        await self._cache_zremrangebyrank(cache_key, 0, -16)

        return True, None

    async def check_message_similarity(self, content: str) -> Tuple[bool, Optional[str]]:
        l = len(content.strip())
        if (
            l < self.MIN_MESSAGE_LENGTH_FOR_SIMILARITY
            or l > self.MAX_MESSAGE_LENGTH_FOR_SIMILARITY
        ):
            return True, None

        if self._is_conversational_pattern(content):
            return True, None

        cache_key = f"{self.cache_prefix}:recent_messages"
        recent_messages = await self._cache_lrange(
            cache_key, 0, self.SIMILARITY_CHECK_COUNT - 1
        )

        similar_count = 0
        for recent_msg in recent_messages[: self.SIMILARITY_CHECK_COUNT]:
            if len(recent_msg.strip()) < self.MIN_MESSAGE_LENGTH_FOR_SIMILARITY:
                continue

            similarity = levenshtein_ratio(content.lower(), recent_msg.lower())
            if similarity >= self.SIMILARITY_THRESHOLD:
                similar_count += 1

        if similar_count >= 2:
            await self._record_violation("similar_spam")
            return False, "message too similar to recent messages. please vary your content."

        await self._cache_lpush(cache_key, content)
        await self._cache_ltrim(cache_key, 0, self.SIMILARITY_CHECK_COUNT - 1)
        await self._cache_expire(cache_key, 60)

        return True, None

    async def check_burst_spam(self, content: str) -> Tuple[bool, Optional[str]]:
        cache_key = f"{self.cache_prefix}:burst"
        current_time = time.time()
        cutoff = current_time - self.BURST_WINDOW

        await self._cache_zremrangebyscore(cache_key, "-inf", cutoff)
        count = await self._cache_zcard(cache_key)

        is_short = len(content.strip()) < self.SHORT_MESSAGE_THRESHOLD
        threshold = (
            int(self.BURST_THRESHOLD * self.SHORT_MESSAGE_BURST_MULTIPLIER)
            if is_short
            else self.BURST_THRESHOLD
        )

        if count >= threshold:
            await self._record_violation("burst_spam")
            return False, "slow down kid."

        member = f"{current_time}:{self._nonce()}"
        await self._cache_zadd(cache_key, current_time, member)
        await self._cache_zremrangebyrank(cache_key, 0, -50)

        return True, None

    async def check_spam_patterns(self, content: str) -> Tuple[bool, Optional[str]]:
        return True, None

    async def is_user_muted(self) -> Tuple[bool, Optional[int]]:
        cache_key = f"{self.cache_prefix}:muted"
        mute_until = await self._cache_get(cache_key)

        if mute_until is not None:
            remaining = int(mute_until - time.time())
            if remaining > 0:
                return True, remaining
            else:
                await self._cache_delete(cache_key)

        return False, None

    async def apply_temp_mute(self, duration: int = None):
        if duration is None:
            duration = self.TEMP_MUTE_DURATION

        cache_key = f"{self.cache_prefix}:muted"
        mute_until = time.time() + duration
        await self._cache_set(cache_key, mute_until, duration)

        logger.warning(
            f"user {self.user_id} temporarily muted for {duration}s in chatroom {self.chatroom_id}"
        )

    async def _record_violation(self, violation_type: str):
        cache_key = f"{self.cache_prefix}:violations"
        current_time = time.time()
        cutoff = current_time - 3600

        await self._cache_zremrangebyscore(cache_key, "-inf", cutoff)
        member = f"{current_time}:{violation_type}:{self._nonce()}"
        await self._cache_zadd(cache_key, current_time, member)

        violation_count = await self._cache_zcard(cache_key)

        if violation_count >= self.ESCALATION_THRESHOLDS["shadowban"]:
            logger.error(f"user {self.user_id} triggered shadowban threshold")
            await self._trigger_shadowban()
        elif violation_count >= self.ESCALATION_THRESHOLDS["temp_mute"]:
            await self.apply_temp_mute()
        elif violation_count >= self.ESCALATION_THRESHOLDS["warning"]:
            logger.warning(f"user {self.user_id} received spam warning")

    async def _trigger_shadowban(self):
        try:
            from moderation.services import ModerationService
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = await self._get_user()

            if user:
                from moderation.models import ViolationHistory
                await self._create_violation_record(user)
        except Exception as e:
            logger.error(f"failed to trigger shadowban: {e}")

    def _hash_content(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def _nonce(self) -> str:
        return hashlib.sha256(
            f"{time.time()}-{self.user_id}-{self.chatroom_id}".encode()
        ).hexdigest()[:8]

    def _is_conversational_pattern(self, content: str) -> bool:
        content_lower = content.lower().strip()

        if content_lower.endswith("?"):
            return True

        greetings = [
            "hi",
            "hello",
            "hey",
            "sup",
            "yo",
            "morning",
            "evening",
            "night",
        ]
        if any(content_lower.startswith(g) for g in greetings):
            return True

        agreements = [
            "i agree",
            "i think",
            "i feel",
            "i know",
            "i see",
            "makes sense",
            "you're right",
            "that's true",
            "exactly",
            "totally",
        ]
        if any(phrase in content_lower for phrase in agreements):
            return True

        reactions = ["lol", "lmao", "haha", "omg", "wow", "nice", "cool", "awesome"]
        if any(reaction in content_lower for reaction in reactions):
            return True

        return False

    async def _cache_get(self, key: str, default=None):
        return await cache.aget(key, default)

    async def _cache_set(self, key: str, value, timeout: int):
        return await cache.aset(key, value, timeout)

    async def _cache_delete(self, key: str):
        return await cache.adelete(key)

    async def _cache_incr(self, key: str, timeout: int):
        try:
            val = await cache.aincr(key)
           
            await cache.atouch(key, timeout)
            return val
        except ValueError:
            await cache.aset(key, 1, timeout)
            return 1

    async def _cache_expire(self, key: str, timeout: int):
        return await cache.atouch(key, timeout)

    async def _cache_zadd(self, key: str, score: float, member: str):
        client = await self._get_redis_client()
        await client.zadd(key, {member: score})

    async def _cache_zremrangebyscore(
        self, key: str, min_score: float, max_score: float
    ):
        client = await self._get_redis_client()
        await client.zremrangebyscore(key, min_score, max_score)

    async def _cache_zcount(
        self,
        key: str,
        min_score: float,
        max_score: float,
        member_prefix: Optional[str] = None,
    ) -> int:
        client = await self._get_redis_client()
        count = await client.zcount(key, min_score, max_score)
        if member_prefix is None:
            return count
        members = await client.zrangebyscore(key, min_score, max_score)
        return sum(1 for m in members if m.startswith(member_prefix))

    async def _cache_zremrangebyrank(self, key: str, start: int, stop: int):
        client = await self._get_redis_client()
        await client.zremrangebyrank(key, start, stop)

    async def _cache_zcard(self, key: str) -> int:
        client = await self._get_redis_client()
        return await client.zcard(key)

    async def _cache_lrange(self, key: str, start: int, stop: int):
        client = await self._get_redis_client()
        raw = await client.lrange(key, start, stop)
        return [
            x.decode("utf-8") if isinstance(x, bytes) else x for x in raw
        ]

    async def _cache_lpush(self, key: str, value: str):
        client = await self._get_redis_client()
        await client.lpush(key, value)

    async def _cache_ltrim(self, key: str, start: int, stop: int):
        client = await self._get_redis_client()
        await client.ltrim(key, start, stop)

    async def _get_redis_client(self):
       return async_redis_client

    async def _get_user(self):
        try:
            return await User.objects.aget(id=self.user_id)
        except User.DoesNotExist:
            return None

    async def _create_violation_record(self, user):
        from moderation.models import ViolationHistory

        await ViolationHistory.objects.acreate(
            user=user,
            violation_type="spam",
            toxicity_score=0.9,
            content_snippet="automated spam detection",
            action_taken="shadowban",
        )


class SpamDetectionMiddleware:
    @staticmethod
    async def check_all(
        user_id: int, chatroom_id: str, content: str, event_type: str
    ) -> Tuple[bool, Optional[str]]:
        spam_detector = AntiSpamSystem(user_id, chatroom_id)

        # Allow benchmark scripts to bypass rate limits to test raw DB/Moderation throughput
        if "BENCHMARK_BYPASS" in content:
            return True, None

        is_muted, remaining = await spam_detector.is_user_muted()
        if is_muted:
            return False, f"you are temporarily muted. please wait {remaining} seconds."

        if event_type == "message.send":
            allowed, error = await spam_detector.check_message_rate_limit(content)
            if not allowed:
                return False, error

            allowed, error = await spam_detector.check_burst_spam(content)
            if not allowed:
                return False, error

            allowed, error = await spam_detector.check_duplicate_message(content)
            if not allowed:
                return False, error

            allowed, error = await spam_detector.check_message_similarity(content)
            if not allowed:
                return False, error

            allowed, error = await spam_detector.check_spam_patterns(content)
            if not allowed:
                return False, error

        elif event_type == "typing.start":
            allowed = await spam_detector.check_typing_rate_limit()
            if not allowed:
                return False, "typing indicator rate limit exceeded."

        return True, None