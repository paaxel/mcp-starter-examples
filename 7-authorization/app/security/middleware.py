from http.client import HTTPException
from urllib.parse import urlparse


class HostOriginValidationMiddleware:
    """
    Middleware to validate the Origin header against allowed hosts.
    Provides DNS rebinding protection.
    """

    def __init__(self, app, allowed_hosts):
        """
        Initialize the middleware.

        Args:
            app: The ASGI application
            allowed_hosts: List of allowed hostnames
        """
        self.app = app
        self.allowed_hosts = set(h.lower() for h in allowed_hosts)

    async def __call__(self, scope, receive, send):
        """
        Process the request and validate the Origin header.

        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            origin = headers.get(b"origin")

            if origin:
                origin = origin.decode().lower()
                parsed = urlparse(origin)

                # Optional: enforce scheme
                if parsed.scheme not in ("http", "https"):
                    raise HTTPException(403, "Invalid Origin")

                # DNS rebinding protection
                if parsed.hostname not in self.allowed_hosts:
                    raise HTTPException(403, "Invalid Origin")

        await self.app(scope, receive, send)