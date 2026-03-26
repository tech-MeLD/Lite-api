from datetime import datetime

from pydantic import BaseModel


class GitHubRepoStats(BaseModel):
    owner: str
    repository: str
    description: str | None
    stars: int
    forks: int
    open_issues: int
    watchers: int
    primary_language: str | None
    default_branch: str
    html_url: str
    updated_at: datetime


class WeatherData(BaseModel):
    latitude: float
    longitude: float
    temperature_celsius: float
    wind_speed_kmh: float
    wind_direction_degrees: float
    weather_code: int
    observed_at: datetime


class WeatherRecordData(WeatherData):
    id: int
    fetched_at: datetime
