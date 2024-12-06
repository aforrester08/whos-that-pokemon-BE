from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_TITLE: str = "Pokemon Quiz API"
    APP_DESCRIPTION: str = "API for Pokemon guessing game"
    APP_VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:4200"]
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    JSON_LOG_FORMAT: bool = True

    class Config:
        env_file = ".env"