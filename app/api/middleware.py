from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.responses import Response

from app.logging_config import get_logger


logger = get_logger("api")


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):
    """
    Journalise chaque requête HTTP.

    Le corps de la requête et le contenu de
    la réponse ne sont jamais journalisés.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[
            [Request],
            Awaitable[Response],
        ],
    ) -> Response:
        request_id = uuid4().hex
        start_time = perf_counter()

        logger.info(
            "request_started "
            "request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(
                request
            )

        except Exception:
            duration_ms = (
                perf_counter() - start_time
            ) * 1000

            logger.exception(
                "request_failed "
                "request_id=%s method=%s "
                "path=%s duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )

            raise

        duration_ms = (
            perf_counter() - start_time
        ) * 1000

        response.headers[
            "X-Request-ID"
        ] = request_id

        logger.info(
            "request_completed "
            "request_id=%s method=%s "
            "path=%s status_code=%s "
            "duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response