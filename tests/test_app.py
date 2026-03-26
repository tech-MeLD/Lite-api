from fastapi.testclient import TestClient

from app.main import app
from app.schemas.external import GitHubRepoStats, WeatherData, WeatherRecordData
from app.services.external_api import get_external_api_service

client = TestClient(app)
API_HEADERS = {"X-API-Key": "change-me-local-dev"}


class MockExternalApiService:
    async def fetch_github_repo_stats(self, owner: str, repo: str) -> GitHubRepoStats:
        return GitHubRepoStats(
            owner=owner,
            repository=repo,
            description="Mock repository",
            stars=100,
            forks=20,
            open_issues=5,
            watchers=10,
            primary_language="Python",
            default_branch="main",
            html_url=f"https://github.com/{owner}/{repo}",
            updated_at="2026-03-26T00:00:00Z",
        )

    async def fetch_weather(self, latitude: float, longitude: float) -> WeatherData:
        return WeatherData(
            latitude=latitude,
            longitude=longitude,
            temperature_celsius=21.5,
            wind_speed_kmh=8.1,
            wind_direction_degrees=180,
            weather_code=1,
            observed_at="2026-03-26T10:00:00Z",
        )

    async def list_weather_history(self, limit: int = 20) -> list[WeatherRecordData]:
        return [
            WeatherRecordData(
                id=1,
                latitude=39.9,
                longitude=116.4,
                temperature_celsius=21.5,
                wind_speed_kmh=8.1,
                wind_direction_degrees=180,
                weather_code=1,
                observed_at="2026-03-26T10:00:00Z",
                fetched_at="2026-03-26T10:05:00Z",
            )
        ]


async def override_external_api_service() -> MockExternalApiService:
    yield MockExternalApiService()


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_github_repo_stats() -> None:
    app.dependency_overrides[get_external_api_service] = override_external_api_service

    response = client.get(
        "/api/v1/external/github/repo-stats?owner=fastapi&repo=fastapi",
        headers=API_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["data"]["repository"] == "fastapi"

    app.dependency_overrides.clear()


def test_weather() -> None:
    app.dependency_overrides[get_external_api_service] = override_external_api_service

    response = client.get("/api/v1/external/weather?latitude=39.9&longitude=116.4", headers=API_HEADERS)

    assert response.status_code == 200
    assert response.json()["data"]["temperature_celsius"] == 21.5

    app.dependency_overrides.clear()


def test_weather_history() -> None:
    app.dependency_overrides[get_external_api_service] = override_external_api_service

    response = client.get("/api/v1/external/weather/history?limit=10", headers=API_HEADERS)

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == 1

    app.dependency_overrides.clear()


def test_api_key_is_required() -> None:
    response = client.get("/api/v1/external/weather?latitude=39.9&longitude=116.4")

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_API_KEY"
