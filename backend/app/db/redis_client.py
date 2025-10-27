"""
Redis client for caching and task queue operations.
"""

import redis
from typing import Optional, Any
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global Redis clients
_cache_client: Optional[redis.Redis] = None
_celery_client: Optional[redis.Redis] = None


def get_cache_client() -> redis.Redis:
    """Get Redis client for caching"""
    global _cache_client
    if _cache_client is None:
        try:
            # Parse Redis URL and update database
            url_parts = settings.REDIS_URL.rsplit('/', 1)
            base_url = url_parts[0]
            cache_url = f"{base_url}/{settings.REDIS_CACHE_DB}"

            _cache_client = redis.from_url(
                cache_url,
                decode_responses=True,
                socket_timeout=5
            )
            # Test connection
            _cache_client.ping()
            logger.info(f"Connected to Redis cache at {cache_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis cache: {e}")
            raise
    return _cache_client


def get_celery_client() -> redis.Redis:
    """Get Redis client for Celery tasks"""
    global _celery_client
    if _celery_client is None:
        try:
            # Parse Redis URL and update database
            url_parts = settings.REDIS_URL.rsplit('/', 1)
            base_url = url_parts[0]
            celery_url = f"{base_url}/{settings.REDIS_CELERY_DB}"

            _celery_client = redis.from_url(
                celery_url,
                decode_responses=True,
                socket_timeout=5
            )
            # Test connection
            _celery_client.ping()
            logger.info(f"Connected to Redis Celery at {celery_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis Celery: {e}")
            raise
    return _celery_client


def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set cache value with TTL"""
    try:
        client = get_cache_client()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error(f"Failed to set cache key '{key}': {e}")
        return False


def get_cache(key: str) -> Optional[Any]:
    """Get cache value"""
    try:
        client = get_cache_client()
        value = client.get(key)
        if value is None:
            return None

        # Try to parse as JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    except Exception as e:
        logger.error(f"Failed to get cache key '{key}': {e}")
        return None


def delete_cache(key: str) -> bool:
    """Delete cache key"""
    try:
        client = get_cache_client()
        return bool(client.delete(key))
    except Exception as e:
        logger.error(f"Failed to delete cache key '{key}': {e}")
        return False


def delete_cache_pattern(pattern: str) -> int:
    """Delete all cache keys matching pattern"""
    try:
        client = get_cache_client()
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Failed to delete cache pattern '{pattern}': {e}")
        return 0


def increment_counter(key: str, ttl: int = 60) -> int:
    """Increment counter with TTL"""
    try:
        client = get_cache_client()
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl)
        result = pipe.execute()
        return result[0]
    except Exception as e:
        logger.error(f"Failed to increment counter '{key}': {e}")
        return 0


def add_to_sorted_set(key: str, member: str, score: float) -> bool:
    """Add member to sorted set"""
    try:
        client = get_cache_client()
        client.zadd(key, {member: score})
        return True
    except Exception as e:
        logger.error(f"Failed to add to sorted set '{key}': {e}")
        return False


def get_top_from_sorted_set(key: str, count: int = 10) -> list:
    """Get top members from sorted set"""
    try:
        client = get_cache_client()
        return client.zrevrange(key, 0, count - 1, withscores=True)
    except Exception as e:
        logger.error(f"Failed to get top from sorted set '{key}': {e}")
        return []


def close_connections():
    """Close Redis connections"""
    global _cache_client, _celery_client
    if _cache_client:
        _cache_client.close()
        _cache_client = None
    if _celery_client:
        _celery_client.close()
        _celery_client = None
    logger.info("Redis connections closed")