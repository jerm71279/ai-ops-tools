"""
OberaConnect Caching Layer

Provides caching with Redis backend and in-memory fallback.
Designed to reduce API calls and improve response times.

Usage:
    from oberaconnect_tools.common.cache import get_cache, cached

    # Get the cache instance
    cache = get_cache()

    # Manual caching
    cache.set("sites", sites_data, ttl=300)  # 5 min TTL
    data = cache.get("sites")

    # Decorator-based caching
    @cached(ttl=300, key_prefix="unifi")
    def get_sites():
        return api.fetch_sites()

Environment Variables:
    REDIS_URL           - Redis connection URL (default: None, uses in-memory)
    CACHE_DEFAULT_TTL   - Default TTL in seconds (default: 300)
    CACHE_ENABLED       - Enable/disable caching (default: true)
"""

import hashlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from threading import Lock
from typing import Any, Callable, Dict, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry:
    """Cache entry with value and expiration."""
    value: Any
    expires_at: float

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass


class InMemoryCache(CacheBackend):
    """
    Thread-safe in-memory cache with TTL support.

    Used as fallback when Redis is not available.
    Not suitable for multi-process deployments.
    """

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl: int) -> bool:
        with self._lock:
            # Evict expired entries if cache is full
            if len(self._cache) >= self._max_size:
                self._evict_expired()

            # Still full? Evict oldest
            if len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            self._cache[key] = CacheEntry(
                value=value,
                expires_at=time.time() + ttl
            )
            return True

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> bool:
        with self._lock:
            self._cache.clear()
            return True

    def exists(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                del self._cache[key]
                return False
            return True

    def _evict_expired(self):
        """Remove expired entries."""
        now = time.time()
        expired = [k for k, v in self._cache.items() if v.expires_at < now]
        for key in expired:
            del self._cache[key]


class RedisCache(CacheBackend):
    """
    Redis-backed cache with automatic serialization.

    Requires redis-py package.
    """

    def __init__(self, redis_url: str):
        try:
            import redis
            self._redis = redis.from_url(redis_url)
            # Test connection
            self._redis.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except ImportError:
            raise ImportError("redis package required. pip install redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self._redis.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception as e:
            logger.warning(f"Redis GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int) -> bool:
        try:
            data = json.dumps(value, default=str)
            self._redis.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.warning(f"Redis SET error: {e}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return self._redis.delete(key) > 0
        except Exception as e:
            logger.warning(f"Redis DELETE error: {e}")
            return False

    def clear(self) -> bool:
        try:
            self._redis.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Redis CLEAR error: {e}")
            return False

    def exists(self, key: str) -> bool:
        try:
            return self._redis.exists(key) > 0
        except Exception as e:
            logger.warning(f"Redis EXISTS error: {e}")
            return False


class Cache:
    """
    Main cache interface with automatic backend selection.

    Uses Redis if REDIS_URL is set, otherwise falls back to in-memory.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 300,
        enabled: bool = True
    ):
        self.default_ttl = default_ttl
        self.enabled = enabled
        self._backend: Optional[CacheBackend] = None

        if not enabled:
            logger.info("Caching disabled")
            return

        # Try Redis first
        redis_url = redis_url or os.getenv('REDIS_URL')
        if redis_url:
            try:
                self._backend = RedisCache(redis_url)
                logger.info("Using Redis cache backend")
                return
            except Exception as e:
                logger.warning(f"Redis unavailable, falling back to in-memory: {e}")

        # Fall back to in-memory
        self._backend = InMemoryCache()
        logger.info("Using in-memory cache backend")

    def get(self, key: str, default: T = None) -> Optional[T]:
        """Get value from cache."""
        if not self.enabled or not self._backend:
            return default
        value = self._backend.get(key)
        return value if value is not None else default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.enabled or not self._backend:
            return False
        return self._backend.set(key, value, ttl or self.default_ttl)

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled or not self._backend:
            return False
        return self._backend.delete(key)

    def clear(self) -> bool:
        """Clear all cache entries."""
        if not self.enabled or not self._backend:
            return False
        return self._backend.clear()

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled or not self._backend:
            return False
        return self._backend.exists(key)

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], T],
        ttl: Optional[int] = None
    ) -> T:
        """Get from cache or compute and store."""
        value = self.get(key)
        if value is not None:
            return value

        value = factory()
        self.set(key, value, ttl)
        return value

    @property
    def backend_type(self) -> str:
        """Get the type of cache backend in use."""
        if not self._backend:
            return "disabled"
        return "redis" if isinstance(self._backend, RedisCache) else "memory"


# Global cache instance
_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = Cache(
            redis_url=os.getenv('REDIS_URL'),
            default_ttl=int(os.getenv('CACHE_DEFAULT_TTL', '300')),
            enabled=os.getenv('CACHE_ENABLED', 'true').lower() != 'false'
        )
    return _cache


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Decorator for caching function results.

    Args:
        ttl: Cache TTL in seconds (None uses default)
        key_prefix: Prefix for cache keys
        key_builder: Custom function to build cache key from args

    Usage:
        @cached(ttl=300, key_prefix="unifi")
        def get_sites():
            return api.fetch_sites()

        @cached(key_builder=lambda site_id: f"site:{site_id}")
        def get_site(site_id: str):
            return api.fetch_site(site_id)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = get_cache()

            # Build cache key
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                # Default: hash of function name + args
                key_data = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
                key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
                key = f"{key_prefix}:{func.__name__}:{key_hash}" if key_prefix else f"{func.__name__}:{key_hash}"

            # Try cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value

            # Compute and cache
            logger.debug(f"Cache miss: {key}")
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result

        return wrapper
    return decorator


def invalidate_pattern(pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern.

    Only works with Redis backend (uses SCAN).
    Returns number of keys deleted.
    """
    cache = get_cache()
    if cache.backend_type != "redis":
        logger.warning("Pattern invalidation only supported with Redis backend")
        return 0

    try:
        # Access underlying Redis client
        redis_client = cache._backend._redis
        count = 0
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
            count += 1
        return count
    except Exception as e:
        logger.error(f"Pattern invalidation failed: {e}")
        return 0


__all__ = [
    'Cache',
    'CacheBackend',
    'InMemoryCache',
    'RedisCache',
    'get_cache',
    'cached',
    'invalidate_pattern'
]
