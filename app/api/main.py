from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.middleware import (
    RequestLoggingMiddleware,
)
from app.api.routes import router
from app.config import settings
from app.logging_config import get_logger


logger = get_logger("startup")


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    """
    Gère le démarrage et l'arrêt de l'API.
    """

    logger.info(
        "application_started "
        "service=%s version=%s "
        "environment=%s",
        settings.application_name,
        settings.application_version,
        settings.environment,
    )

    yield

    logger.info(
        "application_stopped "
        "service=%s",
        settings.application_name,
    )


app = FastAPI(
    title="Semantic Layer Builder API",
    description=(
        "API déterministe pour analyser des sources, "
        "construire un modèle sémantique et générer "
        "un projet LookML validé."
    ),
    version=settings.application_version,
    lifespan=lifespan,
)


app.add_middleware(
    RequestLoggingMiddleware
)

app.include_router(router)


@app.get(
    "/",
    tags=["Root"],
)
def root() -> dict[str, str]:
    """
    Présente le service et ses principaux chemins.
    """

    return {
        "service": settings.application_name,
        "version": settings.application_version,
        "environment": settings.environment,
        "documentation": "/docs",
        "health": "/health",
    }
