from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx

from app.core.config import get_settings
from app.core.exceptions import UpstreamServiceError
from app.schemas.external import GitHubRepoStats, WeatherData


class ExternalApiService:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def fetch_github_repo_stats(self, owner: str, repo: str) -> GitHubRepoStats:
        url = f"{get_settings().github_api_base_url}/repos/{owner}/{repo}"
        try:
            response = await self._client.get(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "fastapi-standard-template",
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise UpstreamServiceError("GitHub API", exc.response.text, exc.response.status_code) from exc
        except httpx.HTTPError as exc:
            raise UpstreamServiceError("GitHub API", str(exc)) from exc

        payload = response.json()
        return GitHubRepoStats(
            owner=payload["owner"]["login"],
            repository=payload["name"],
            description=payload["description"],
            stars=payload["stargazers_count"],
            forks=payload["forks_count"],
            open_issues=payload["open_issues_count"],
            watchers=payload["subscribers_count"],
            primary_language=payload["language"],
            default_branch=payload["default_branch"],
            html_url=payload["html_url"],
            updated_at=payload["updated_at"],
        )

    async def fetch_weather(self, latitude: float, longitude: float) -> WeatherData:
        url = f"{get_settings().weather_api_base_url}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
        }
        try:
            response = await self._client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise UpstreamServiceError("Weather API", exc.response.text, exc.response.status_code) from exc
        except httpx.HTTPError as exc:
            raise UpstreamServiceError("Weather API", str(exc)) from exc

        payload = response.json()
        current_weather = payload["current_weather"]

        return WeatherData(
            latitude=payload["latitude"],
            longitude=payload["longitude"],
            temperature_celsius=current_weather["temperature"],
            wind_speed_kmh=current_weather["windspeed"],
            wind_direction_degrees=current_weather["winddirection"],
            weather_code=current_weather["weathercode"],
            observed_at=current_weather["time"],
        )


@asynccontextmanager
async def external_api_client() -> AsyncIterator[httpx.AsyncClient]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        yield client


async def get_external_api_service() -> AsyncIterator[ExternalApiService]:
    async with external_api_client() as client:
        yield ExternalApiService(client)
