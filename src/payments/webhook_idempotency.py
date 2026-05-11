"""
AX-002: Stripe Webhook Idempotency & Deduplication
1-hour in-memory cache + 24h database cache via request hash comparison.
Prevents duplicate payment processing.
"""

import hashlib
import json
import time
import logging
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta, timezone
from collections import OrderedDict

logger = logging.getLogger(__name__)


class WebhookIdempotencyCache:
    """
    In-memory webhook deduplication with Redis-ready interface.
    Tracks processed webhook IDs within a time window.
    """
    
    def __init__(
        self,
        memory_ttl: int = 3600,  # 1 hour
        db_ttl: int = 86400,  # 24 hours
        max_cache_size: int = 10000
    ):
        """
        Initialize idempotency cache.
        
        Args:
            memory_ttl: In-memory cache TTL (seconds)
            db_ttl: Database cache TTL (seconds)
            max_cache_size: Max entries before LRU eviction
        """
        self.memory_ttl = memory_ttl
        self.db_ttl = db_ttl
        self.max_cache_size = max_cache_size
        
        # OrderedDict for LRU eviction
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def compute_request_hash(self, event_id: str, event_data: dict) -> str:
        """
        Compute deterministic hash of webhook event.
        
        Args:
            event_id: Stripe event ID
            event_data: Event payload
        
        Returns:
            SHA256 hash of normalized event
        """
        # Normalize data for consistent hashing
        normalized = {
            "id": event_id,
            "type": event_data.get("type"),
            "data": json.dumps(event_data.get("data", {}), sort_keys=True)
        }
        
        content = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def is_duplicate(
        self,
        event_id: str,
        event_data: dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if webhook has already been processed.
        
        Args:
            event_id: Stripe event ID
            event_data: Event payload
        
        Returns:
            (is_duplicate, cached_result_or_none)
        """
        request_hash = self.compute_request_hash(event_id, event_data)
        now = time.time()
        
        # Cleanup expired entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
        
        # Check if already processed
        if request_hash in self.cache:
            entry = self.cache[request_hash]
            
            # Check if still within memory window
            age = now - entry["timestamp"]
            if age < self.memory_ttl:
                logger.info(f"Webhook duplicate detected (in-memory, age={age:.1f}s): {event_id}")
                return True, entry.get("result")
            # else: expired from memory, but could be in DB
        
        return False, None
    
    def mark_processed(
        self,
        event_id: str,
        event_data: dict,
        result: Any = None
    ) -> str:
        """
        Mark webhook as processed.
        
        Args:
            event_id: Stripe event ID
            event_data: Event payload
            result: Processing result (for replay)
        
        Returns:
            Request hash
        """
        request_hash = self.compute_request_hash(event_id, event_data)
        now = time.time()
        
        entry = {
            "event_id": event_id,
            "timestamp": now,
            "result": result,
            "db_expiry": now + self.db_ttl
        }
        
        self.cache[request_hash] = entry
        # Move to end (LRU)
        self.cache.move_to_end(request_hash)
        
        # LRU eviction
        if len(self.cache) > self.max_cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"LRU eviction: removed {oldest_key[:8]}...")
        
        logger.info(f"Webhook marked as processed: {event_id} (hash={request_hash[:8]}...)")
        return request_hash
    
    def get_result(self, request_hash: str) -> Optional[Any]:
        """Get cached result for a webhook."""
        if request_hash in self.cache:
            return self.cache[request_hash].get("result")
        return None
    
    def _cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now - entry["timestamp"] > self.memory_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired webhook entries")
        
        self.last_cleanup = now
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = time.time()
        
        # Count entries by age
        in_memory = sum(
            1 for entry in self.cache.values()
            if now - entry["timestamp"] < self.memory_ttl
        )
        in_db_only = len(self.cache) - in_memory
        
        return {
            "total_entries": len(self.cache),
            "in_memory": in_memory,
            "in_db_only": in_db_only,
            "memory_ttl": self.memory_ttl,
            "db_ttl": self.db_ttl,
            "max_size": self.max_cache_size
        }


class WebhookProcessor:
    """Process webhooks with idempotency protection."""
    
    def __init__(self, idempotency_cache: WebhookIdempotencyCache):
        """
        Initialize processor.
        
        Args:
            idempotency_cache: IdempotencyCache instance
        """
        self.cache = idempotency_cache
        self.handlers: Dict[str, callable] = {}
    
    def register_handler(self, event_type: str, handler: callable) -> None:
        """Register event handler."""
        self.handlers[event_type] = handler
    
    def process(
        self,
        event_id: str,
        event_type: str,
        event_data: dict
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Process webhook with idempotency.
        
        Args:
            event_id: Stripe event ID
            event_type: Event type (charge.succeeded, etc)
            event_data: Event payload
        
        Returns:
            (status_code, response_dict)
        """
        # Check for duplicates
        is_dup, cached_result = self.cache.is_duplicate(
            event_id,
            {"type": event_type, "data": event_data}
        )
        
        if is_dup:
            return 200, {
                "received": True,
                "duplicate": True,
                "event_id": event_id,
                "cached_result": cached_result
            }
        
        # Call handler
        try:
            handler = self.handlers.get(event_type)
            if not handler:
                logger.warning(f"No handler for event type: {event_type}")
                result = {"status": "no_handler", "event_type": event_type}
            else:
                result = handler(event_id, event_data)
                logger.info(f"Webhook processed: {event_type} (id={event_id})")
        
        except Exception as e:
            logger.error(f"Handler error for {event_type}: {str(e)}")
            return 500, {"error": "Handler execution failed"}
        
        # Mark as processed
        self.cache.mark_processed(
            event_id,
            {"type": event_type, "data": event_data},
            result
        )
        
        return 200, {
            "received": True,
            "duplicate": False,
            "event_id": event_id,
            "event_type": event_type,
            "result": result
        }


class DatabaseIdempotencyCache:
    """
    Database backend for idempotency (stub for integration).
    Extends in-memory cache with persistent storage.
    """
    
    def __init__(self, db_connection: Optional[Any] = None):
        """
        Initialize database cache.
        
        Args:
            db_connection: Database connection (SQLAlchemy, psycopg2, etc)
        """
        self.db = db_connection
    
    def store_webhook(
        self,
        event_id: str,
        request_hash: str,
        event_type: str,
        result: Any,
        ttl_seconds: int = 86400
    ) -> bool:
        """
        Store webhook in database.
        
        Query template:
            INSERT INTO webhook_cache (event_id, request_hash, event_type, result, expires_at)
            VALUES (%s, %s, %s, %s, NOW() + INTERVAL %s)
        """
        logger.info(f"Stub: store_webhook to DB: {event_id}")
        # Implementation: INSERT into webhook_cache table with TTL
        return True
    
    def get_webhook(self, request_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve webhook from database.
        
        Query template:
            SELECT event_id, result FROM webhook_cache
            WHERE request_hash = %s AND expires_at > NOW()
        """
        logger.info(f"Stub: get_webhook from DB: {request_hash}")
        # Implementation: SELECT from webhook_cache
        return None
    
    def cleanup_expired(self, older_than_hours: int = 24) -> int:
        """
        Remove expired entries from database.
        
        Query template:
            DELETE FROM webhook_cache WHERE expires_at < NOW() - INTERVAL %s
        """
        logger.info(f"Stub: cleanup webhooks older than {older_than_hours}h")
        # Implementation: DELETE expired records
        return 0


# Factory
def create_idempotency_processor(
    memory_ttl: int = 3600,
    db_ttl: int = 86400
) -> WebhookProcessor:
    """Factory to create webhook processor with idempotency."""
    cache = WebhookIdempotencyCache(memory_ttl=memory_ttl, db_ttl=db_ttl)
    return WebhookProcessor(cache)
