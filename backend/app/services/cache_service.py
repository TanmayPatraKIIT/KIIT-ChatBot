"""
Cache service for storing query responses and reducing LLM calls.
Uses Redis for fast in-memory caching with TTL support.
"""

import hashlib
import json
from typing import Optional, Any, List
import logging

from app.db.redis_client import (
    get_cache,
    set_cache,
    delete_cache,
    delete_cache_pattern,
    increment_counter,
    add_to_sorted_set,
    get_top_from_sorted_set
)

logger = logging.getLogger(__name__)


class CacheService:
    """Service for managing cached responses and query tracking"""

    # Cache key prefixes
    RESPONSE_PREFIX = "chat:response:"
    POPULAR_QUERIES_KEY = "chat:popular_queries"
    SCRAPER_LAST_RUN_PREFIX = "scraper:last_run:"
    RATE_LIMIT_PREFIX = "rate_limit:"

    def __init__(self):
        self.default_ttl = 3600  # 1 hour

    def _generate_query_hash(self, query: str) -> str:
        """
        Generate hash for query to use as cache key.

        Args:
            query: User query string

        Returns:
            Hash string
        """
        # Normalize query (lowercase, strip whitespace)
        normalized = query.lower().strip()

        # Generate SHA-256 hash
        hash_obj = hashlib.sha256(normalized.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # Use first 16 chars for brevity

    def get_cached_response(self, query: str) -> Optional[dict]:
        """
        Get cached response for query.

        Args:
            query: User query

        Returns:
            Cached response dict or None if not found
        """
        try:
            query_hash = self._generate_query_hash(query)
            cache_key = f"{self.RESPONSE_PREFIX}{query_hash}"

            cached = get_cache(cache_key)

            if cached:
                logger.info(f"Cache HIT for query: {query[:50]}...")
                return cached
            else:
                logger.debug(f"Cache MISS for query: {query[:50]}...")
                return None

        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None

    def set_cached_response(
        self,
        query: str,
        response: str,
        sources: List[dict],
        query_time_ms: int,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache query response.

        Args:
            query: User query
            response: Bot response
            sources: List of source references
            query_time_ms: Query execution time
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if cached successfully
        """
        try:
            query_hash = self._generate_query_hash(query)
            cache_key = f"{self.RESPONSE_PREFIX}{query_hash}"

            cache_data = {
                "query": query,
                "response": response,
                "sources": sources,
                "query_time_ms": query_time_ms,
                "from_cache": True
            }

            ttl = ttl or self.default_ttl
            success = set_cache(cache_key, cache_data, ttl=ttl)

            if success:
                logger.debug(f"Cached response for query: {query[:50]}... (TTL: {ttl}s)")

                # Track popular query
                self.track_query(query)

            return success

        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False

    def invalidate_cache_for_notice_type(self, notice_type: str) -> int:
        """
        Invalidate all cached responses related to a notice type.
        Called when new notices of that type are scraped.

        Args:
            notice_type: Notice type (general, exam, academic, holiday)

        Returns:
            Number of keys deleted
        """
        try:
            # Delete all response caches (simpler approach)
            # In production, could track which queries relate to which types
            pattern = f"{self.RESPONSE_PREFIX}*"
            deleted = delete_cache_pattern(pattern)

            logger.info(f"Invalidated {deleted} cached responses for notice type: {notice_type}")
            return deleted

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return 0

    def invalidate_all_response_cache(self) -> int:
        """
        Invalidate all cached responses.

        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"{self.RESPONSE_PREFIX}*"
            deleted = delete_cache_pattern(pattern)

            logger.info(f"Invalidated all {deleted} cached responses")
            return deleted

        except Exception as e:
            logger.error(f"Error invalidating all cache: {e}")
            return 0

    def track_query(self, query: str):
        """
        Track query frequency for analytics.

        Args:
            query: User query
        """
        try:
            # Normalize query
            normalized = query.lower().strip()

            # Increment score in sorted set
            add_to_sorted_set(self.POPULAR_QUERIES_KEY, normalized, 1)

        except Exception as e:
            logger.error(f"Error tracking query: {e}")

    def get_popular_queries(self, count: int = 10) -> List[tuple]:
        """
        Get most popular queries.

        Args:
            count: Number of queries to return

        Returns:
            List of (query, count) tuples
        """
        try:
            return get_top_from_sorted_set(self.POPULAR_QUERIES_KEY, count)

        except Exception as e:
            logger.error(f"Error getting popular queries: {e}")
            return []

    def cache_popular_queries(self, queries: List[str], ttl: int = 86400):
        """
        Pre-cache responses for popular queries.
        Called by background task.

        Args:
            queries: List of popular queries to cache
            ttl: Cache TTL (default: 24 hours)
        """
        logger.info(f"Pre-caching {len(queries)} popular queries")

        # This would be called with actual responses from RAG service
        # For now, just log the intent
        for query in queries:
            logger.debug(f"Would pre-cache: {query}")

    def set_scraper_last_run(self, source_type: str, timestamp: str) -> bool:
        """
        Store last scraper run timestamp.

        Args:
            source_type: Type of source (general, exam, etc.)
            timestamp: ISO timestamp

        Returns:
            True if stored successfully
        """
        try:
            key = f"{self.SCRAPER_LAST_RUN_PREFIX}{source_type}"
            return set_cache(key, timestamp, ttl=None)  # No expiration

        except Exception as e:
            logger.error(f"Error setting scraper last run: {e}")
            return False

    def get_scraper_last_run(self, source_type: str) -> Optional[str]:
        """
        Get last scraper run timestamp.

        Args:
            source_type: Type of source

        Returns:
            ISO timestamp string or None
        """
        try:
            key = f"{self.SCRAPER_LAST_RUN_PREFIX}{source_type}"
            return get_cache(key)

        except Exception as e:
            logger.error(f"Error getting scraper last run: {e}")
            return None

    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 60) -> tuple:
        """
        Check if request is within rate limit.

        Args:
            identifier: IP address or user ID
            limit: Max requests per window
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed: bool, current_count: int)
        """
        try:
            key = f"{self.RATE_LIMIT_PREFIX}{identifier}"
            count = increment_counter(key, ttl=window)

            is_allowed = count <= limit

            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {identifier}: {count}/{limit}")

            return is_allowed, count

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # On error, allow request but log
            return True, 0

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        try:
            # Get popular queries
            popular = self.get_popular_queries(5)

            return {
                "popular_queries": [
                    {"query": q, "count": int(c)} for q, c in popular
                ],
                "cache_enabled": True
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "error": str(e),
                "cache_enabled": False
            }


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get cache service singleton"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
