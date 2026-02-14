from fastmcp.server.auth import OIDCProxy
from app.config import Config
from app.storage import get_encrypted_store



def get_auth_proxy() -> OIDCProxy:
    """Create and return an OIDC authentication proxy."""
    return OIDCProxy(
        config_url=f"{Config.ISSUER}/.well-known/openid-configuration",
        client_id=Config.CLIENT_ID,
        client_secret=Config.CLIENT_SECRET,
        base_url=Config.MCP_BASE_URL,
        redirect_path="/auth/callback",

        client_storage=get_encrypted_store()
    )


def has_role(role: str):
    """
    Create an authorization checker that validates if the user has a specific role.
    This function consider the provider is Keycloak and checks the "realm_access" claim for roles.

    Args:
        role: The role name to check for

    Returns:
        A function that checks if the context token contains the specified role
    """

    def check(ctx) -> bool:
        token = ctx.token
        roles = [x.lower() for x in token.claims.get("realm_access", {}).get("roles", [])]
        return role.lower() in roles

    return check