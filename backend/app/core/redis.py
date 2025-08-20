import logging
from typing import Optional, Any
import json
import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from app.config import REDIS_SETTINGS

logger = logging.getLogger(__name__)


class RedisManager:
    """Production-ready Redis manager with connection pooling"""

    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[redis.Redis] = None

    async def initialize(self):
        """Initialize Redis connection pool"""
        if self._pool is not None:
            return

        try:
            # Create connection pool
            self._pool = ConnectionPool.from_url(
                REDIS_SETTINGS.redis_url,
                max_connections=REDIS_SETTINGS.redis_max_connections,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Create Redis client
            self._redis = redis.Redis(connection_pool=self._pool)

            # Test connection
            await self._redis.ping()
            logger.info("Redis initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def close(self):
        """Clean shutdown of Redis connections"""
        if self._redis:
            await self._redis.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connections closed")

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            value = await self._redis.get(key)
            return value.decode() if value else None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with optional TTL"""
        try:
            result = await self._redis.set(key, value, ex=ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            result = await self._redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            result = await self._redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set JSON value in Redis"""
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, ttl)
        except Exception as e:
            logger.error(f"Redis SET_JSON error for key {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from Redis"""
        try:
            value = await self.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis GET_JSON error for key {key}: {e}")
            return None

    async def health_check(self) -> bool:
        """Health check for Redis connectivity"""
        try:
            response = await self._redis.ping()
            return response is True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Global Redis manager instance
redis_manager = RedisManager()
