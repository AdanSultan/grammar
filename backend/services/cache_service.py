import json
import hashlib
import asyncio
from typing import Optional, Any, Dict
import aioredis
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.cache_ttl = 3600  # 1 hour default TTL
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.redis = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    def _generate_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """Generate cache key from data"""
        # Create a deterministic string representation
        data_str = json.dumps(data, sort_keys=True)
        # Generate hash
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, prefix: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached data"""
        if not self.redis:
            return None
        
        try:
            key = self._generate_key(prefix, data)
            cached_data = await self.redis.get(key)
            
            if cached_data:
                logger.info(f"Cache hit for key: {key}")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache miss for key: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, prefix: str, data: Dict[str, Any], result: Dict[str, Any], ttl: int = None) -> bool:
        """Set cached data"""
        if not self.redis:
            return False
        
        try:
            key = self._generate_key(prefix, data)
            ttl = ttl or self.cache_ttl
            
            await self.redis.setex(
                key,
                ttl,
                json.dumps(result)
            )
            
            logger.info(f"Cached data for key: {key} with TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, prefix: str, data: Dict[str, Any]) -> bool:
        """Delete cached data"""
        if not self.redis:
            return False
        
        try:
            key = self._generate_key(prefix, data)
            await self.redis.delete(key)
            logger.info(f"Deleted cache for key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def clear_all(self, prefix: str = None) -> bool:
        """Clear all cached data or by prefix"""
        if not self.redis:
            return False
        
        try:
            if prefix:
                pattern = f"{prefix}:*"
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cache entries with prefix: {prefix}")
            else:
                await self.redis.flushdb()
                logger.info("Cleared all cache")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis:
            return {"connected": False}
        
        try:
            info = await self.redis.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"connected": False, "error": str(e)}

# Global cache instance
cache_service = CacheService()

# Cache decorator
def cache_result(prefix: str, ttl: int = None):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create cache key from function arguments
            cache_data = {
                "args": args,
                "kwargs": kwargs
            }
            
            # Try to get from cache
            cached_result = await cache_service.get(prefix, cache_data)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache_service.set(prefix, cache_data, result, ttl)
            
            return result
        
        return wrapper
    return decorator 