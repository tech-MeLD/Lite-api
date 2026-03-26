from fastapi import APIRouter

from app.api.routes import external, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(external.router, prefix="/external", tags=["external"])
