from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./typeform.db"
    # Comma-separated list of allowed origins. Set this in your Render env vars
    # to include your Vercel frontend URL e.g. https://your-app.vercel.app
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    APP_ENV: str = "development"

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",")]
        # In production, also always allow the wildcard for flexibility
        return origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
