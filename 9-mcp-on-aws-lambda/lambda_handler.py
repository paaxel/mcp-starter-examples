from mangum import Mangum

from main import configure_middleware, create_app

mcp = create_app()
app = mcp.http_app(json_response=True)
configure_middleware(app)

handler = Mangum(app, lifespan="auto")
