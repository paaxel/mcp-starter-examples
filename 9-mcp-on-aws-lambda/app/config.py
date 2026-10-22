import os


class Config:
    """Application configuration."""

    # Server settings
    HOST = os.getenv("MCP_HOST", "localhost")
    PORT = int(os.getenv("MCP_PORT", "8000"))

    # DynamoDB settings (shared store for session state)
    DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "mcp-sessions")
    AWS_REGION = os.getenv("AWS_REGION")

    # Session state TTL in seconds
    SESSION_MIN_TTL = 0
    SESSION_MAX_TTL = 86400
    SESSION_MISSING_TTL = 3600

    # Shared key so every replica can validate and resume multi-round tools.
    # Must be at least 32 bytes; leave unset for single-process runs.
    # In AWS, the key is read at runtime from the secret ARN below, never from
    # the function configuration. REQUEST_STATE_KEY is for local development only.
    REQUEST_STATE_KEY = os.getenv("REQUEST_STATE_KEY")
    REQUEST_STATE_SECRET_ARN = os.getenv("REQUEST_STATE_SECRET_ARN")

    # CORS settings
    ALLOWED_ORIGINS = [
        "127.0.0.1",
        "localhost"
    ]
