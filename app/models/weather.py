from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class WeatherRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    latitude: float = Field(index=True)
    longitude: float = Field(index=True)
    temperature_celsius: float
    wind_speed_kmh: float
    wind_direction_degrees: float
    weather_code: int
    observed_at: datetime
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
