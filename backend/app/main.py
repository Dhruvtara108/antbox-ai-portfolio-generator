from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.portfolio import router as portfolio_router
from app.services.template_service import TEMPLATE_PATH


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
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/template.html", include_in_schema=False)
def template() -> FileResponse:
    return FileResponse(TEMPLATE_PATH, media_type="text/html")
