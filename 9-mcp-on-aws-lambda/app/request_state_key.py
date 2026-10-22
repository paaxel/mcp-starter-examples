from functools import lru_cache

import boto3

from .config import Config


@lru_cache(maxsize=1)
def get_request_state_key() -> bytes | None:
    """
    Return the request-state signing key, or None for single-process runs.

    In AWS the key is fetched from Secrets Manager at runtime, so it never
    appears in the function configuration. The result is cached per Lambda
    instance to avoid a Secrets Manager call on every request.
    """
    if Config.REQUEST_STATE_KEY:
        return Config.REQUEST_STATE_KEY.encode()

    if not Config.REQUEST_STATE_SECRET_ARN:
        return None

    client = boto3.client("secretsmanager", region_name=Config.AWS_REGION)
    response = client.get_secret_value(SecretId=Config.REQUEST_STATE_SECRET_ARN)
    return response["SecretString"].encode()
