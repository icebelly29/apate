import os
from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    # Uploads / limits
    MAX_UPLOAD_MB: int = 200
    ALLOWED_EXTS: str = "mp4,mov,mkv,webm,avi,flv"
    DEFAULT_FPS: float = 1.0
    CANONICAL_WIDTH: int = 1280  # 720p default
    CANONICAL_HEIGHT: int = 720

    # Paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "uploads")
    RESULTS_DIR: str = os.getenv("RESULTS_DIR", "results")

    # Celery / Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    # API
    BASE_EXTERNAL_URL: str = os.getenv("BASE_EXTERNAL_URL", "http://localhost:8000")

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.RESULTS_DIR, exist_ok=True)
