from cryptography.fernet import Fernet
from key_value.aio.stores.redis import RedisStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
from .config import Config


def get_redis_store() -> RedisStore:
    """Create and return a Redis store instance."""
    return RedisStore(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT
    )


def get_fernet_cipher() -> Fernet:
    """Create and return a Fernet cipher instance."""
    return Fernet(Config.FERNET_KEY)


def get_encrypted_store() -> FernetEncryptionWrapper:
    """Create and return an encrypted key-value store."""
    store = get_redis_store()
    fernet = get_fernet_cipher()
    return FernetEncryptionWrapper(key_value=store, fernet=fernet)