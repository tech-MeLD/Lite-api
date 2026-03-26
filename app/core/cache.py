from redis.asyncio import Redis

from app.core.config import get_settings

_redis_client: Redis | None = None


def init_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        return

    settings = get_settings()
    _redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> Redis | None:
    if _redis_client is None:
        init_redis()
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
    _redis_client = None
