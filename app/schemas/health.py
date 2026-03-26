from pydantic import BaseModel


class DependencyStatus(BaseModel):
    status: str
    detail: str | None = None


class HealthStatusData(BaseModel):
    status: str
    services: dict[str, DependencyStatus]
