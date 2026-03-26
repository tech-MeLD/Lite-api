import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request

from app.api.router import api_router
from app.core.cache import close_redis, init_redis
from app.core.config import get_settings
from app.core.database import close_engine, init_db
from app.core.exceptions import add_exception_handlers
from app.core.http import close_http_client, init_http_client
from app.core.logging import configure_logging
from app.core.request_context import reset_request_id, set_request_id

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.app_env == "production" and settings.api_key == "change-me-local-dev":
        raise RuntimeError("API_KEY must be overridden in production")
    init_http_client()
    init_redis()
    await init_db()
    yield
    await close_http_client()
    await close_redis()
    await close_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
        version="1.0.0",
        lifespan=lifespan,
    )
    add_exception_handlers(app)

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        token = set_request_id(request_id)
        request.state.request_id = request_id
        started_at = perf_counter()
        logger.info("request.started method=%s path=%s", request.method, request.url.path)
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request.failed method=%s path=%s", request.method, request.url.path)
            reset_request_id(token)
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request.completed method=%s path=%s status_code=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        reset_request_id(token)
        return response

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
