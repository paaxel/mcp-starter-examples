import os


class Config:
    """Application configuration."""

    # Server settings
    HOST = os.getenv("MCP_HOST", "localhost")
    PORT = int(os.getenv("MCP_PORT", "8000"))

    # Redis settings (shared store for session state)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Session state TTL in seconds
    SESSION_MIN_TTL = 0
    SESSION_MAX_TTL = 86400
    SESSION_MISSING_TTL = 3600

    # Shared key so every replica can validate and resume multi-round tools.
    # Must be at least 32 bytes; leave unset for single-process runs.
    REQUEST_STATE_KEY = os.getenv("REQUEST_STATE_KEY")

    # CORS settings
    ALLOWED_ORIGINS = [
        "127.0.0.1",
        "localhost"
    ]
