from key_value.aio.stores.redis import RedisStore
from key_value.aio.wrappers.ttl_clamp import TTLClampWrapper

from .config import Config


def get_session_state_store() -> TTLClampWrapper:
    """Create the Redis-backed session state store with default TTLs."""
    store = RedisStore(url=Config.REDIS_URL)
    return TTLClampWrapper(
        store,
        min_ttl=Config.SESSION_MIN_TTL,
        max_ttl=Config.SESSION_MAX_TTL,
        missing_ttl=Config.SESSION_MISSING_TTL,
    )
