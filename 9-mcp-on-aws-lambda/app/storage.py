from key_value.aio.stores.dynamodb import DynamoDBStore
from key_value.aio.wrappers.ttl_clamp import TTLClampWrapper

from .config import Config


def get_session_state_store() -> TTLClampWrapper:
    """Create the DynamoDB-backed session state store with default TTLs."""
    # The table is provisioned by CloudFormation (collection/key schema, TTL on "ttl")
    store = DynamoDBStore(
        table_name=Config.DYNAMODB_TABLE_NAME,
        region_name=Config.AWS_REGION,
        auto_create=False,
    )
    return TTLClampWrapper(
        store,
        min_ttl=Config.SESSION_MIN_TTL,
        max_ttl=Config.SESSION_MAX_TTL,
        missing_ttl=Config.SESSION_MISSING_TTL,
    )
