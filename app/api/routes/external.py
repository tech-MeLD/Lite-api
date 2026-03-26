from fastapi import APIRouter, Depends, Query

from app.schemas.common import ApiResponse
from app.schemas.external import GitHubRepoStats, WeatherData
from app.services.external_api import ExternalApiService, get_external_api_service

router = APIRouter()


@router.get("/github/repo-stats", response_model=ApiResponse[GitHubRepoStats])
async def get_github_repo_stats(
    owner: str = Query(..., min_length=1, description="GitHub repository owner"),
    repo: str = Query(..., min_length=1, description="GitHub repository name"),
    service: ExternalApiService = Depends(get_external_api_service),
) -> ApiResponse[GitHubRepoStats]:
    data = await service.fetch_github_repo_stats(owner=owner, repo=repo)
    return ApiResponse(message="GitHub repository statistics fetched successfully", data=data)


@router.get("/weather", response_model=ApiResponse[WeatherData])
async def get_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: ExternalApiService = Depends(get_external_api_service),
) -> ApiResponse[WeatherData]:
    data = await service.fetch_weather(latitude=latitude, longitude=longitude)
    return ApiResponse(message="Weather data fetched successfully", data=data)
