"""
Events API endpoints.

Handles tag event ingestion and retrieval.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.models.schemas import TagPayload
from app.core.database import get_events_collection
from app.utils.helpers import event_helper

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest")
async def ingest_tag_event(payload: TagPayload) -> Dict[str, Any]:
    """
    Receive and store tag telemetry data.
    
    Args:
        payload: Tag telemetry data
        
    Returns:
        Success response with document ID
        
    Raises:
        HTTPException: If database is not connected or insertion fails
    """
    collection = get_events_collection()
    
    if collection is None:
        raise HTTPException(
            status_code=500,
            detail="Database not connected"
        )
    
    try:
        data = payload.model_dump()
        # Convert timestamp string to datetime object
        data['timestamp'] = datetime.fromisoformat(payload.timestamp)
        
        result = await collection.insert_one(data)
        
        logger.info(f"Stored event from tag {payload.tag_id} (ID: {result.inserted_id})")
        
        return {
            "status": "success",
            "doc_id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error storing event: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store event: {str(e)}"
        )


@router.get("")
async def get_events(limit: int = 20) -> Dict[str, Any]:
    """
    Retrieve recent tag events.
    
    Args:
        limit: Maximum number of events to return (default: 20)
        
    Returns:
        List of recent events sorted by timestamp descending
        
    Raises:
        HTTPException: If database is not connected or query fails
    """
    collection = get_events_collection()
    
    if collection is None:
        raise HTTPException(
            status_code=500,
            detail="Database not connected"
        )
    
    try:
        events = []
        cursor = collection.find().sort("timestamp", -1).limit(limit)
        
        async for event in cursor:
            events.append(event_helper(event))
        
        return {
            "status": "success",
            "events": events
        }
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch events: {str(e)}"
        )

