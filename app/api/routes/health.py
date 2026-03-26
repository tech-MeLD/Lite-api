from fastapi import APIRouter, Response, status

from app.api.docs import DEPENDENCY_UNHEALTHY_RESPONSE
from app.core.cache import check_redis_health
from app.core.database import check_database_health
from app.schemas.common import ApiResponse
from app.schemas.health import DependencyStatus, HealthStatusData

router = APIRouter()


@router.get(
    "/health",
    response_model=ApiResponse[dict],
    responses={
        200: {
            "description": "Application liveness check",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Service is healthy",
                        "data": {"status": "ok"},
                    }
                }
            },
        }
    },
)
async def health_check() -> ApiResponse[dict]:
    return ApiResponse(message="Service is healthy", data={"status": "ok"})


@router.get(
    "/health/dependencies",
    response_model=ApiResponse[HealthStatusData],
    responses={
        200: {
            "description": "All dependencies are healthy",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Dependency health check completed",
                        "data": {
                            "status": "ok",
                            "services": {
                                "redis": {"status": "ok", "detail": None},
                                "sqlite": {"status": "ok", "detail": None},
                            },
                        },
                    }
                }
            },
        },
        503: DEPENDENCY_UNHEALTHY_RESPONSE,
    },
)
async def dependency_health_check(response: Response) -> ApiResponse[HealthStatusData]:
    redis_status, redis_detail = await check_redis_health()
    sqlite_status, sqlite_detail = await check_database_health()

    overall_status = "ok" if redis_status == "ok" and sqlite_status == "ok" else "degraded"
    response.status_code = status.HTTP_200_OK if overall_status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE

    payload = HealthStatusData(
        status=overall_status,
        services={
            "redis": DependencyStatus(status=redis_status, detail=redis_detail),
            "sqlite": DependencyStatus(status=sqlite_status, detail=sqlite_detail),
        },
    )
    return ApiResponse(message="Dependency health check completed", data=payload)
