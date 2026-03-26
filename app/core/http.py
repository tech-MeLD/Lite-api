import httpx

from app.core.config import get_settings

_http_client: httpx.AsyncClient | None = None


def init_http_client() -> None:
    global _http_client
    if _http_client is not None:
        return

    settings = get_settings()
    _http_client = httpx.AsyncClient(timeout=settings.request_timeout_seconds)


def get_http_client() -> httpx.AsyncClient:
    if _http_client is None:
        init_http_client()
    if _http_client is None:
        raise RuntimeError("HTTP client is not initialized")
    return _http_client


async def close_http_client() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
    _http_client = None
