from functools import lru_cache
import logging
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
logger = logging.getLogger(__name__)

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(WORKSPACE_ROOT / ".env")


class Settings(BaseSettings):
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    gemini_model: str = "gemini-3.8-flash"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    logger.info(
        "Gemini configuration loaded",
        extra={
            "gemini_configured": settings.gemini_configured,
            "gemini_model": settings.gemini_model,
            "project_env_exists": (PROJECT_ROOT / ".env").is_file(),
            "workspace_env_exists": (WORKSPACE_ROOT / ".env").is_file(),
        },
    )
    return settings
