from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[dict])
async def health_check() -> ApiResponse[dict]:
    return ApiResponse(message="Service is healthy", data={"status": "ok"})
