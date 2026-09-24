import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from app.config import get_settings
from app.routes.portfolio import router as portfolio_router
from app.services.template_service import TEMPLATE_PATH


logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            response = await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404:
                raise
            return FileResponse(FRONTEND_DIST / "index.html")
        return response


settings = get_settings()
app = FastAPI(title="Antbox AI Portfolio Generator", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(portfolio_router)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "gemini_configured": bool(settings.gemini_api_key.strip()),
    }


@app.get("/template.html", include_in_schema=False)
def template() -> FileResponse:
    return FileResponse(TEMPLATE_PATH, media_type="text/html")


if FRONTEND_DIST.is_dir() and (FRONTEND_DIST / "index.html").is_file():
    app.mount("/", SPAStaticFiles(directory=FRONTEND_DIST), name="frontend")
else:
    logger.warning(
        "Frontend build not found at %s; build frontend/dist before serving the frontend.",
        FRONTEND_DIST,
    )
