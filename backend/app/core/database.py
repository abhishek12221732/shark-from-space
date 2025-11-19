"""
Database connection and collection access.

Handles MongoDB connection using Motor (async MongoDB driver).
"""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from .config import settings

logger = logging.getLogger(__name__)

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """
    Get the MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase instance or None if connection failed
    """
    global _client, _db
    
    if _db is not None:
        return _db
    
    if _client is None:
        try:
            _client = AsyncIOMotorClient(settings.mongo_connection_string)
            _db = _client.shark_database
            logger.info("Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return None
    
    return _db


def get_events_collection() -> Optional[AsyncIOMotorCollection]:
    """
    Get the events collection.
    
    Returns:
        AsyncIOMotorCollection for events or None if database not connected
    """
    db = get_database()
    if db is None:
        return None
    return db.get_collection("events")


def get_hotspots_collection() -> Optional[AsyncIOMotorCollection]:
    """
    Get the hotspots collection.
    
    Returns:
        AsyncIOMotorCollection for hotspots or None if database not connected
    """
    db = get_database()
    if db is None:
        return None
    return db.get_collection("hotspots")


def close_database() -> None:
    """Close the database connection."""
    global _client, _db
    
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("Database connection closed")

