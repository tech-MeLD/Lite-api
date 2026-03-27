import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast

import httpx
from fastapi import Depends
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.cache import get_redis
from app.core.config import get_settings
from app.core.database import get_session
from app.core.exceptions import UpstreamServiceError
from app.core.http import get_http_client
from app.models.weather import WeatherRecord
from app.schemas.external import GitHubRepoStats, WeatherData, WeatherRecordData

logger = logging.getLogger(__name__)


class ExternalApiService:
    def __init__(
        self,
        client: httpx.AsyncClient,
        redis_client: Redis | None,
        session: AsyncSession,
    ) -> None:
        self._client = client
        self._redis = redis_client
        self._session = session

    async def fetch_github_repo_stats(self, owner: str, repo: str) -> GitHubRepoStats:
        cache_key = f"github:repo:{owner.lower()}:{repo.lower()}"
        cached_value = await self._get_cached_value(cache_key)
        if cached_value is not None:
            return GitHubRepoStats.model_validate_json(cached_value)

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
            raise UpstreamServiceError(
                "GitHub API",
                exc.response.text,
                exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise UpstreamServiceError("GitHub API", str(exc)) from exc

        payload = response.json()
        repo_stats = GitHubRepoStats(
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
        await self._set_cached_value(
            cache_key,
            repo_stats.model_dump_json(),
            get_settings().github_cache_ttl_seconds,
        )
        return repo_stats

    async def fetch_weather(self, latitude: float, longitude: float) -> WeatherData:
        cached_record = await self._get_latest_weather_record(
            latitude=latitude,
            longitude=longitude,
        )
        if cached_record is not None:
            return self._weather_record_to_schema(cached_record)

        url = f"{get_settings().weather_api_base_url}/forecast"
        params: dict[str, str | float] = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
        }
        try:
            response = await self._client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise UpstreamServiceError(
                "Weather API",
                exc.response.text,
                exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise UpstreamServiceError("Weather API", str(exc)) from exc

        payload = response.json()
        current_weather = payload["current_weather"]

        weather_data = WeatherData(
            latitude=payload["latitude"],
            longitude=payload["longitude"],
            temperature_celsius=current_weather["temperature"],
            wind_speed_kmh=current_weather["windspeed"],
            wind_direction_degrees=current_weather["winddirection"],
            weather_code=current_weather["weathercode"],
            observed_at=current_weather["time"],
        )
        await self._save_weather_record(weather_data)
        return weather_data

    async def list_weather_history(self, limit: int = 20) -> list[WeatherRecordData]:
        statement = (
            select(WeatherRecord)
            .order_by(cast(Any, WeatherRecord.fetched_at).desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        records = result.scalars().all()
        return [self._weather_record_to_history(record) for record in records]

    async def _get_cached_value(self, key: str) -> str | None:
        if self._redis is None:
            return None
        try:
            return await self._redis.get(key)
        except RedisError:
            logger.warning("redis.get_failed key=%s", key, exc_info=True)
            return None

    async def _set_cached_value(self, key: str, value: str, ttl_seconds: int) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.set(key, value, ex=ttl_seconds)
        except RedisError:
            logger.warning("redis.set_failed key=%s", key, exc_info=True)

    async def _get_latest_weather_record(
        self,
        latitude: float,
        longitude: float,
    ) -> WeatherRecord | None:
        statement = (
            select(WeatherRecord)
            .where(WeatherRecord.latitude == latitude)
            .where(WeatherRecord.longitude == longitude)
            .order_by(cast(Any, WeatherRecord.fetched_at).desc())
            .limit(1)
        )
        result = await self._session.execute(statement)
        record = result.scalars().first()
        if record is None:
            return None

        fetched_at = self._normalize_datetime(record.fetched_at)
        age_seconds = (datetime.now(UTC) - fetched_at).total_seconds()
        if age_seconds > get_settings().weather_cache_ttl_seconds:
            return None
        return record

    async def _save_weather_record(self, weather_data: WeatherData) -> None:
        record = WeatherRecord(**weather_data.model_dump())
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)

    @staticmethod
    def _weather_record_to_schema(record: WeatherRecord) -> WeatherData:
        return WeatherData(
            latitude=record.latitude,
            longitude=record.longitude,
            temperature_celsius=record.temperature_celsius,
            wind_speed_kmh=record.wind_speed_kmh,
            wind_direction_degrees=record.wind_direction_degrees,
            weather_code=record.weather_code,
            observed_at=record.observed_at,
        )

    @staticmethod
    def _weather_record_to_history(record: WeatherRecord) -> WeatherRecordData:
        return WeatherRecordData(
            id=record.id or 0,
            latitude=record.latitude,
            longitude=record.longitude,
            temperature_celsius=record.temperature_celsius,
            wind_speed_kmh=record.wind_speed_kmh,
            wind_direction_degrees=record.wind_direction_degrees,
            weather_code=record.weather_code,
            observed_at=record.observed_at,
            fetched_at=record.fetched_at,
        )

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


async def get_external_api_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncIterator[ExternalApiService]:
    yield ExternalApiService(
        client=get_http_client(),
        redis_client=get_redis(),
        session=session,
    )
