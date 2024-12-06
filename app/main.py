from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.logging import setup_logging
from app.config import Settings
from app.api import pokemon_router
from app.middleware.logging_middleware import LoggingMiddleware

def create_app(settings: Settings = Settings()) -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(LoggingMiddleware)

    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE,
        json_format=settings.JSON_LOG_FORMAT
    )

    app.include_router(pokemon_router, prefix="/api/v1")

    return app

app = create_app()
