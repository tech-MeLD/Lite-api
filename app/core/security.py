from typing import Annotated

from fastapi import Header, status

from app.core.config import get_settings
from app.core.exceptions import ApiException, ErrorCode


async def verify_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None) -> None:
    settings = get_settings()
    if not x_api_key or x_api_key != settings.api_key:
        raise ApiException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.INVALID_API_KEY,
            message="Invalid or missing API key",
        )
