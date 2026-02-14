import uvicorn
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from app.config import Config
from app.security.auth import get_auth_proxy
from app.security.middleware import HostOriginValidationMiddleware
from app.mcp_endpoints.routes import register_routes


def create_app() -> FastMCP:
    """
    Create and configure the FastMCP application.

    Returns:
        Configured FastMCP instance
    """
    # Initialize FastMCP with authentication
    mcp = FastMCP(
        name="PersonalNoteManager",
        auth=get_auth_proxy()
    )

    # Register all routes (tools, resources, prompts)
    register_routes(mcp)

    return mcp


def configure_middleware(app):
    """
    Configure middleware for the application.

    Args:
        app: The ASGI application to configure
    """
    # Custom Origin validation FIRST (before CORS)
    # Executed at each request on the backend side
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
    # Create MCP application
    mcp = create_app()

    # Get HTTP app
    app = mcp.http_app()

    # Configure middleware
    configure_middleware(app)

    # Run the server
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)


if __name__ == "__main__":
    main()