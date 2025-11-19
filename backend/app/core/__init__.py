"""
Core application configuration and setup.
"""

from .config import settings
from .database import get_database, get_events_collection, get_hotspots_collection

__all__ = [
    "settings",
    "get_database",
    "get_events_collection",
    "get_hotspots_collection",
]

