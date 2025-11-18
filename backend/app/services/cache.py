"""
Simple in-memory cache using cachetools
"""
from cachetools import TTLCache
from app.config import settings
import time


class SimpleCache:
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=settings.CACHE_TTL)
        self.rate_limits = {}
    
    def get(self, key: str):
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value, ttl: int = None):
        """Set value in cache"""
        self.cache[key] = value
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def check_rate_limit(self, client_ip: str, limit: int = 100, window: int = 60):
        """Check rate limit for client IP"""
        now = time.time()
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Remove old requests outside the window
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if now - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[client_ip]) >= limit:
            return False, len(self.rate_limits[client_ip])
        
        # Add current request
        self.rate_limits[client_ip].append(now)
        return True, len(self.rate_limits[client_ip])


# Global instance
cache = SimpleCache()
