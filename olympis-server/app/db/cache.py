from typing import Optional, Protocol, runtime_checkable

import redis.asyncio as redis

from app.config import REDIS_DB, REDIS_HOST, REDIS_PORT
from app.logger import get_logger

logger = get_logger(__name__)


# Protocol class since the redis client is redis specific
# This allows for quick cache changes without changing code outside of this file
@runtime_checkable
class Cache(Protocol):
    async def get(self, key: str) -> Optional[str]: ...
    async def set(
        self,
        key: str,
        value: str,
    ) -> bool: ...
    async def delete(self, *keys: str) -> int: ...
    async def exists(self, *keys: str) -> int: ...
    async def close(self) -> None: ...


class RedisCache:
    def __init__(self, client: redis.Redis):
        self._client = client
        logger.info("RedisCache initialized")

    async def get(self, key: str) -> Optional[str]:
        logger.info(f"Getting value for key: {key}")
        try:
            value = await self._client.get(key)
            logger.info(f"Successfully retrieved value for key: {key}")
            return value
        except Exception as e:
            logger.exception(f"Error getting value for key: {key}")
            raise

    async def set(
        self,
        key: str,
        value: str,
    ) -> bool:
        logger.info(f"Setting value for key: {key}")
        try:
            result = await self._client.set(key, value)
            logger.info(f"Successfully set value for key: {key}")
            return result
        except Exception as e:
            logger.exception(f"Error setting value for key: {key}")
            raise

    async def delete(self, *keys: str) -> int:
        logger.info(f"Deleting keys: {keys}")
        try:
            result = await self._client.delete(*keys)
            logger.info(f"Successfully deleted {result} keys")
            return result
        except Exception as e:
            logger.exception(f"Error deleting keys: {keys}")
            raise

    async def exists(self, *keys: str) -> int:
        logger.info(f"Checking existence of keys: {keys}")
        try:
            result = await self._client.exists(*keys)
            logger.info(f"Found {result} existing keys")
            return result
        except Exception as e:
            logger.exception(f"Error checking existence of keys: {keys}")
            raise

    async def close(self) -> None:
        logger.info("Closing Redis connection")
        try:
            await self._client.aclose()
            logger.info("Redis connection closed successfully")
        except Exception as e:
            logger.exception("Error closing Redis connection")
            raise


def init_cache() -> Cache:
    logger.info(f"Initializing cache connection to {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    try:
        client = redis.Redis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}", decode_responses=True
        )
        logger.info("Cache connection established successfully")
        return RedisCache(client)
    except Exception as e:
        logger.exception("Failed to initialize cache connection")
        raise
