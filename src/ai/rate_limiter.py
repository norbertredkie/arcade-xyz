"""
AX-004: AI Service Rate Limiter for Claude API
Per-user limits: 5/min, 100/hr, 500/day
24-hour response cache (50% cost reduction) with exponential backoff.
"""

import time
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Tuple, Deque
from collections import deque, defaultdict
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration."""
    
    # Per-user limits
    PER_MINUTE = 5
    PER_HOUR = 100
    PER_DAY = 500
    
    # Windows (seconds)
    MINUTE_WINDOW = 60
    HOUR_WINDOW = 3600
    DAY_WINDOW = 86400
    
    # Cache
    CACHE_TTL = 86400  # 24 hours


class RateLimiter:
    """
    Multi-tier rate limiter with cache.
    Tracks requests per user at minute/hour/day granularity.
    """
    
    def __init__(self, config: RateLimitConfig = None):
        """
        Initialize rate limiter.
        
        Args:
            config: RateLimitConfig instance
        """
        self.config = config or RateLimitConfig()
        
        # Tracking: {user_id: deque([timestamp, ...])}
        self.minute_requests: Dict[str, Deque] = defaultdict(deque)
        self.hour_requests: Dict[str, Deque] = defaultdict(deque)
        self.day_requests: Dict[str, Deque] = defaultdict(deque)
        
        # Backoff tracking: {user_id: (backoff_until_ts, attempt_count)}
        self.backoff: Dict[str, Tuple[float, int]] = {}
        
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def check_limits(self, user_id: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Check if user is within rate limits.
        
        Returns:
            (allowed, limits_dict, error_message)
        """
        now = time.time()
        
        # Lazy cleanup
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
        
        # Check backoff
        if user_id in self.backoff:
            backoff_until, attempts = self.backoff[user_id]
            if now < backoff_until:
                retry_after = int(backoff_until - now) + 1
                return False, {}, f"Rate limited (exponential backoff). Retry after {retry_after}s"
            else:
                # Backoff window expired
                del self.backoff[user_id]
        
        # Prune old entries
        self._prune_old_requests(user_id, now)
        
        # Count requests
        minute_count = len(self.minute_requests[user_id])
        hour_count = len(self.hour_requests[user_id])
        day_count = len(self.day_requests[user_id])
        
        limits = {
            "minute": {"count": minute_count, "limit": self.config.PER_MINUTE},
            "hour": {"count": hour_count, "limit": self.config.PER_HOUR},
            "day": {"count": day_count, "limit": self.config.PER_DAY},
            "reset_minute": self.config.MINUTE_WINDOW,
            "reset_hour": self.config.HOUR_WINDOW,
            "reset_day": self.config.DAY_WINDOW,
        }
        
        # Check violations
        if minute_count >= self.config.PER_MINUTE:
            self._apply_backoff(user_id, 1)  # 1-second backoff first
            return False, limits, "Minute rate limit exceeded"
        
        if hour_count >= self.config.PER_HOUR:
            self._apply_backoff(user_id, 5)  # 5-second backoff
            return False, limits, "Hour rate limit exceeded"
        
        if day_count >= self.config.PER_DAY:
            self._apply_backoff(user_id, 60)  # 1-minute backoff
            return False, limits, "Day rate limit exceeded"
        
        return True, limits, None
    
    def mark_request(self, user_id: str) -> None:
        """Record a request for the user."""
        now = time.time()
        
        self.minute_requests[user_id].append(now)
        self.hour_requests[user_id].append(now)
        self.day_requests[user_id].append(now)
        
        logger.debug(f"Request marked for {user_id}")
    
    def _apply_backoff(self, user_id: str, base_seconds: int) -> None:
        """
        Apply exponential backoff.
        
        Args:
            user_id: User ID
            base_seconds: Base backoff duration (1, 5, 60 seconds)
        """
        now = time.time()
        
        if user_id in self.backoff:
            _, attempts = self.backoff[user_id]
            attempts += 1
        else:
            attempts = 1
        
        # Exponential backoff: base * 2^(attempts-1)
        backoff_seconds = base_seconds * (2 ** (attempts - 1))
        backoff_seconds = min(backoff_seconds, 3600)  # Cap at 1 hour
        
        backoff_until = now + backoff_seconds
        self.backoff[user_id] = (backoff_until, attempts)
        
        logger.warning(f"Exponential backoff applied to {user_id}: {backoff_seconds}s (attempt {attempts})")
    
    def _prune_old_requests(self, user_id: str, now: float) -> None:
        """Remove requests outside their windows."""
        minute_cutoff = now - self.config.MINUTE_WINDOW
        hour_cutoff = now - self.config.HOUR_WINDOW
        day_cutoff = now - self.config.DAY_WINDOW
        
        # Minute window
        while self.minute_requests[user_id] and self.minute_requests[user_id][0] < minute_cutoff:
            self.minute_requests[user_id].popleft()
        
        # Hour window
        while self.hour_requests[user_id] and self.hour_requests[user_id][0] < hour_cutoff:
            self.hour_requests[user_id].popleft()
        
        # Day window
        while self.day_requests[user_id] and self.day_requests[user_id][0] < day_cutoff:
            self.day_requests[user_id].popleft()
    
    def _cleanup_expired(self) -> None:
        """Clean up idle users."""
        now = time.time()
        day_cutoff = now - self.config.DAY_WINDOW
        
        # Remove users with no recent requests
        idle_users = [
            uid for uid, deq in self.day_requests.items()
            if not deq or deq[-1] < day_cutoff
        ]
        
        for uid in idle_users:
            del self.minute_requests[uid]
            del self.hour_requests[uid]
            del self.day_requests[uid]
        
        if idle_users:
            logger.debug(f"Cleaned up {len(idle_users)} idle users")
        
        self.last_cleanup = now
    
    def get_status(self, user_id: str) -> Dict[str, Any]:
        """Get rate limit status for a user."""
        now = time.time()
        self._prune_old_requests(user_id, now)
        
        limits = {
            "user_id": user_id,
            "minute": {
                "count": len(self.minute_requests[user_id]),
                "limit": self.config.PER_MINUTE,
                "remaining": max(0, self.config.PER_MINUTE - len(self.minute_requests[user_id]))
            },
            "hour": {
                "count": len(self.hour_requests[user_id]),
                "limit": self.config.PER_HOUR,
                "remaining": max(0, self.config.PER_HOUR - len(self.hour_requests[user_id]))
            },
            "day": {
                "count": len(self.day_requests[user_id]),
                "limit": self.config.PER_DAY,
                "remaining": max(0, self.config.PER_DAY - len(self.day_requests[user_id]))
            }
        }
        
        if user_id in self.backoff:
            backoff_until, attempts = self.backoff[user_id]
            limits["backoff"] = {
                "active": now < backoff_until,
                "retry_after": int(max(0, backoff_until - now)) + 1,
                "attempts": attempts
            }
        
        return limits


class ResponseCache:
    """
    24-hour response cache for AI requests.
    Reduces cost by 50% on duplicate queries.
    """
    
    def __init__(self, ttl_seconds: int = 86400, max_size: int = 10000):
        """
        Initialize response cache.
        
        Args:
            ttl_seconds: Cache TTL (24 hours default)
            max_size: Max cache entries
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.last_cleanup = time.time()
    
    def compute_request_hash(
        self,
        user_id: str,
        message: str,
        context: Optional[str] = None
    ) -> str:
        """
        Compute deterministic hash of request.
        
        Returns:
            SHA256 hash
        """
        normalized = {
            "user_id": user_id,
            "message": message.strip(),
            "context": (context or "").strip()
        }
        content = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response.
        
        Returns:
            Cached response or None
        """
        if cache_key not in self.cache:
            return None
        
        entry = self.cache[cache_key]
        now = time.time()
        
        if now - entry["timestamp"] > self.ttl_seconds:
            del self.cache[cache_key]
            return None
        
        logger.debug(f"Cache hit: {cache_key[:8]}...")
        return entry["response"]
    
    def set(
        self,
        cache_key: str,
        response: Dict[str, Any]
    ) -> None:
        """Store response in cache."""
        now = time.time()
        
        self.cache[cache_key] = {
            "timestamp": now,
            "response": response
        }
        
        # LRU cleanup if cache is full
        if len(self.cache) > self.max_size:
            oldest_key = min(
                (k for k in self.cache.keys()),
                key=lambda k: self.cache[k]["timestamp"]
            )
            del self.cache[oldest_key]
            logger.debug(f"LRU eviction: removed {oldest_key[:8]}...")
        
        logger.debug(f"Response cached: {cache_key[:8]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = time.time()
        valid_entries = sum(
            1 for entry in self.cache.values()
            if now - entry["timestamp"] < self.ttl_seconds
        )
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "max_size": self.max_size,
            "ttl_hours": self.ttl_seconds // 3600
        }


# Factory
def create_ai_rate_limiter() -> RateLimiter:
    """Factory to create configured AI rate limiter."""
    return RateLimiter()


def create_response_cache() -> ResponseCache:
    """Factory to create response cache."""
    return ResponseCache()
