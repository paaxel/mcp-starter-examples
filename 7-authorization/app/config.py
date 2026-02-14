import base64
import hashlib
import os


class Config:
    """Application configuration."""
    def derive_fernet_key(input_string: str) -> bytes:
        # 1. Hash the string to get exactly 32 bytes
        digest = hashlib.sha256(input_string.encode()).digest()
        # 2. Base64 encode it for Fernet compatibility
        return base64.urlsafe_b64encode(digest)

        # Server settings
    HOST = os.getenv("MCP_HOST", "localhost")
    PORT = int(os.getenv("MCP_PORT", "8000"))

    # OAuth/OIDC settings
    ISSUER = os.getenv("OAUTH_ISSUER", "http://localhost:8085/realms/mcp-sample-realm")
    CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
    CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

    # Base URL
    MCP_BASE_URL = f"http://{HOST}:{PORT}"

    # Encryption settings
    FERNET_KEY = os.getenv("FERNET_KEY")
    FERNET_KEY = derive_fernet_key(FERNET_KEY)

    # Redis settings
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

    # Storage path
    FILE_PATH = 'c:/PersonalNoteManagerStorage/notes.txt'

    # CORS settings
    ALLOWED_ORIGINS = [
        "127.0.0.1",
        "localhost"
    ]
