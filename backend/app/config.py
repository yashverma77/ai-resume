from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg2://resume:resume@db:5432/resume_screening",
        alias="DATABASE_URL",
    )
    upload_dir: Path = Field(default=Path("/data/uploads"), alias="UPLOAD_DIR")
    max_upload_mb: int = Field(default=15, alias="MAX_UPLOAD_MB")
    worker_poll_seconds: int = Field(default=3, alias="WORKER_POLL_SECONDS")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
