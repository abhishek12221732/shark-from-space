"""
Main FastAPI application.

This is the entry point for the Shark Foraging Project API.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import get_database, close_database
from app.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    
    # Test database connection
    db = get_database()
    if db is None:
        logger.warning("Database connection failed - some features may be unavailable")
    else:
        logger.info("Database connection established")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    close_database()


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API for shark habitat prediction and tracking",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Backward compatibility: include routes without prefix for existing frontend
from app.api.endpoints import events, hotspots
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(hotspots.router, prefix="/hotspots", tags=["hotspots"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API status."""
    db_status = "connected" if get_database() is not None else "disconnected"
    return {
        "status": "connected",
        "message": "Shark Foraging Project API",
        "version": settings.api_version,
        "database": db_status
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = get_database() is not None
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        reload_dirs=["app"]
    )

