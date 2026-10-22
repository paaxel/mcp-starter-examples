from fastmcp import FastMCP
from fastmcp.server.sessions import SessionProvider

from app.mcp_endpoints.notes import register_note_routes


def register_routes(mcp: FastMCP):
    """
    Register all MCP routes (tools, resources, prompts) with the FastMCP instance.

    Args:
        mcp: FastMCP instance
    """
    mcp.add_provider(SessionProvider())
    register_note_routes(mcp)
