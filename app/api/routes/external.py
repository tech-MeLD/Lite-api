from fastapi import APIRouter, Depends, Query

from app.api.docs import UNAUTHORIZED_RESPONSE, UPSTREAM_ERROR_RESPONSE, VALIDATION_ERROR_RESPONSE
from app.schemas.common import ApiResponse
from app.schemas.external import GitHubRepoStats, WeatherData, WeatherRecordData
from app.services.external_api import ExternalApiService, get_external_api_service

router = APIRouter()


@router.get(
    "/github/repo-stats",
    response_model=ApiResponse[GitHubRepoStats],
    responses={
        200: {
            "description": "GitHub repository statistics fetched successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "GitHub repository statistics fetched successfully",
                        "data": {
                            "owner": "fastapi",
                            "repository": "fastapi",
                            "description": (
                                "FastAPI framework, high performance, easy to learn, "
                                "fast to code, ready for production"
                            ),
                            "stars": 90000,
                            "forks": 8000,
                            "open_issues": 120,
                            "watchers": 1500,
                            "primary_language": "Python",
                            "default_branch": "master",
                            "html_url": "https://github.com/fastapi/fastapi",
                            "updated_at": "2026-03-26T12:00:00Z",
                        },
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        502: UPSTREAM_ERROR_RESPONSE,
    },
)
async def get_github_repo_stats(
    owner: str = Query(..., min_length=1, description="GitHub repository owner"),
    repo: str = Query(..., min_length=1, description="GitHub repository name"),
    service: ExternalApiService = Depends(get_external_api_service),
) -> ApiResponse[GitHubRepoStats]:
    data = await service.fetch_github_repo_stats(owner=owner, repo=repo)
    return ApiResponse(message="GitHub repository statistics fetched successfully", data=data)


@router.get(
    "/weather",
    response_model=ApiResponse[WeatherData],
    responses={
        200: {
            "description": "Weather data fetched successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Weather data fetched successfully",
                        "data": {
                            "latitude": 39.9042,
                            "longitude": 116.4074,
                            "temperature_celsius": 22.5,
                            "wind_speed_kmh": 8.1,
                            "wind_direction_degrees": 180,
                            "weather_code": 1,
                            "observed_at": "2026-03-26T10:00:00Z",
                        },
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        502: UPSTREAM_ERROR_RESPONSE,
    },
)
async def get_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: ExternalApiService = Depends(get_external_api_service),
) -> ApiResponse[WeatherData]:
    data = await service.fetch_weather(latitude=latitude, longitude=longitude)
    return ApiResponse(message="Weather data fetched successfully", data=data)


@router.get(
    "/weather/history",
    response_model=ApiResponse[list[WeatherRecordData]],
    responses={
        200: {
            "description": "Weather history fetched successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Weather history fetched successfully",
                        "data": [
                            {
                                "id": 1,
                                "latitude": 39.9042,
                                "longitude": 116.4074,
                                "temperature_celsius": 22.5,
                                "wind_speed_kmh": 8.1,
                                "wind_direction_degrees": 180,
                                "weather_code": 1,
                                "observed_at": "2026-03-26T10:00:00Z",
                                "fetched_at": "2026-03-26T10:05:00Z",
                            }
                        ],
                    }
                }
            },
        },
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
async def get_weather_history(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return",
    ),
    service: ExternalApiService = Depends(get_external_api_service),
) -> ApiResponse[list[WeatherRecordData]]:
    data = await service.list_weather_history(limit=limit)
    return ApiResponse(message="Weather history fetched successfully", data=data)
