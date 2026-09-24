import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app


class ApiPrefixMiddleware:
    """Normalize requests when the hosting platform forwards the /api prefix."""

    def __init__(self, application):
        self.application = application

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and (
            scope["path"] == "/api" or scope["path"].startswith("/api/")
        ):
            path = scope["path"][4:] or "/"
            if not path.startswith("/"):
                path = "/" + path
            scope = dict(scope)
            scope["path"] = path
            scope["raw_path"] = path.encode("utf-8")
            root_path = scope.get("root_path") or ""
            scope["root_path"] = root_path if root_path.endswith("/api") else root_path + "/api"
        await self.application(scope, receive, send)


app.add_middleware(ApiPrefixMiddleware)


__all__ = ["app"]
