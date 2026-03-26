from fastapi import APIRouter, Depends

from app.api.routes import external, health
from app.core.security import verify_api_key

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    external.router,
    prefix="/external",
    tags=["external"],
    dependencies=[Depends(verify_api_key)],
)
