"""
Redis Cache Service for GyanForge
Handles caching of user modules, content, and session data
"""

import redis
import json
import os
from typing import Any, Optional, Dict
from datetime import timedelta

class RedisService:
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("   Falling back to in-memory cache")
            self.redis_client = None
            self._memory_cache = {}
    
    def set(self, key: str, value: Any, expire_time: int = 3600) -> bool:
        """
        Set a value in cache with expiration time
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire_time: Expiration time in seconds (default 1 hour)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                serialized_value = json.dumps(value, default=str)
                return self.redis_client.setex(key, expire_time, serialized_value)
            else:
                # Fallback to memory cache
                self._memory_cache[key] = {
                    'value': value,
                    'expires_at': expire_time  # Simple implementation
                }
                return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        try:
            if self.redis_client:
                cached_value = self.redis_client.get(key)
                if cached_value:
                    return json.loads(cached_value)
                return None
            else:
                # Fallback to memory cache
                if key in self._memory_cache:
                    return self._memory_cache[key]['value']
                return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache
        
        Args:
            key: Cache key to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                # Fallback to memory cache
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
                return False
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache
        
        Args:
            key: Cache key to check
        
        Returns:
            True if key exists, False otherwise
        """
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                # Fallback to memory cache
                return key in self._memory_cache
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def clear_user_cache(self, user_id: int) -> bool:
        """
        Clear all cached data for a specific user
        
        Args:
            user_id: User ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            pattern = f"user:{user_id}:*"
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return bool(self.redis_client.delete(*keys))
                return True
            else:
                # Fallback to memory cache
                keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(f"user:{user_id}:")]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                return True
        except Exception as e:
            print(f"Clear user cache error: {e}")
            return False
    
    def cache_user_modules(self, user_id: int, modules: list) -> bool:
        """
        Cache user's modules
        
        Args:
            user_id: User ID
            modules: List of user modules
        
        Returns:
            True if successful, False otherwise
        """
        key = f"user:{user_id}:modules"
        return self.set(key, modules, expire_time=1800)  # 30 minutes
    
    def get_user_modules(self, user_id: int) -> Optional[list]:
        """
        Get cached user modules
        
        Args:
            user_id: User ID
        
        Returns:
            List of modules or None if not cached
        """
        key = f"user:{user_id}:modules"
        return self.get(key)
    
    def cache_module_content(self, module_id: int, content: dict) -> bool:
        """
        Cache module content
        
        Args:
            module_id: Module ID
            content: Module content
        
        Returns:
            True if successful, False otherwise
        """
        key = f"module:{module_id}:content"
        return self.set(key, content, expire_time=3600)  # 1 hour
    
    def get_module_content(self, module_id: int) -> Optional[dict]:
        """
        Get cached module content
        
        Args:
            module_id: Module ID
        
        Returns:
            Module content or None if not cached
        """
        key = f"module:{module_id}:content"
        return self.get(key)
    
    def cache_youtube_videos(self, topic: str, videos: list) -> bool:
        """
        Cache YouTube video recommendations for a topic
        
        Args:
            topic: Learning topic
            videos: List of video recommendations
        
        Returns:
            True if successful, False otherwise
        """
        key = f"youtube:{topic.lower().replace(' ', '_')}"
        return self.set(key, videos, expire_time=7200)  # 2 hours
    
    def get_youtube_videos(self, topic: str) -> Optional[list]:
        """
        Get cached YouTube videos for a topic
        
        Args:
            topic: Learning topic
        
        Returns:
            List of videos or None if not cached
        """
        key = f"youtube:{topic.lower().replace(' ', '_')}"
        return self.get(key)

# Create global Redis service instance
redis_service = RedisService()
