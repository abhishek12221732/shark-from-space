"""
API routes and endpoints.
"""

from fastapi import APIRouter

from .endpoints import events, hotspots, simulator

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(hotspots.router, prefix="/hotspots", tags=["hotspots"])
api_router.include_router(simulator.router, prefix="/simulator", tags=["simulator"])

__all__ = ["api_router"]

