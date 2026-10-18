import uvicorn
from fastmcp import FastMCP
from mcp.server.request_state import RequestStateSecurity
from starlette.middleware.cors import CORSMiddleware

from app.config import Config
from app.mcp_endpoints import register_routes
from app.security.middleware import HostOriginValidationMiddleware
from app.storage import get_session_state_store


def create_app() -> FastMCP:
    """
    Create and configure the FastMCP application.

    Returns:
        Configured FastMCP instance
    """
    extra_kwargs = {}
    if Config.REQUEST_STATE_KEY:
        extra_kwargs["request_state_security"] = RequestStateSecurity(
            keys=[Config.REQUEST_STATE_KEY.encode()]
        )

    # Session state lives in Redis, so any replica can serve any request
    mcp = FastMCP(
        name="PersonalNoteManager",
        session_state_store=get_session_state_store(),
        **extra_kwargs,
    )

    register_routes(mcp)

    return mcp


def configure_middleware(app):
    """
    Configure middleware for the application.

    Args:
        app: The ASGI application to configure
    """
    # Custom Origin validation FIRST (before CORS)
    app.add_middleware(
        HostOriginValidationMiddleware,
        allowed_hosts=Config.ALLOWED_ORIGINS
    )

    # Then CORS for legitimate requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"]
    )


def main():
    """Main entry point for running the server."""
    mcp = create_app()

    app = mcp.http_app()

    configure_middleware(app)

    uvicorn.run(app, host=Config.HOST, port=Config.PORT)


if __name__ == "__main__":
    main()
