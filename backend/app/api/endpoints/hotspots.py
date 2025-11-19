"""
Hotspots API endpoints.

Handles ML prediction hotspot data retrieval.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.core.database import get_hotspots_collection
from app.services.ml_predictor import generate_real_hotspots
from app.utils.helpers import hotspot_helper

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_hotspots() -> Dict[str, Any]:
    """
    Retrieve simulated hotspot predictions from MongoDB.
    
    Returns:
        List of hotspot predictions from database
        
    Raises:
        HTTPException: If database is not connected or query fails
    """
    collection = get_hotspots_collection()
    
    if collection is None:
        raise HTTPException(
            status_code=500,
            detail="Database not connected"
        )
    
    try:
        hotspots = []
        cursor = collection.find()
        
        async for hotspot in cursor:
            hotspots.append(hotspot_helper(hotspot))
        
        return {
            "status": "success",
            "hotspots": hotspots
        }
        
    except Exception as e:
        logger.error(f"Error fetching hotspots: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch hotspots: {str(e)}"
        )


@router.get("/real")
async def get_real_hotspots() -> Dict[str, Any]:
    """
    Generate and return real ML predictions for hotspots.
    
    Uses the trained XGBoost model and satellite GeoTIFF data (MODIS Chlorophyll
    and NOAA Pathfinder SST) to generate predictions for a 40×40 grid.
    
    Results are cached per application lifetime for performance.
    
    Returns:
        List of hotspot predictions with latitude, longitude, and prediction_value
        
    Raises:
        HTTPException: If model/data files are missing or prediction fails
    """
    try:
        logger.info("Generating real ML predictions for hotspots")
        predictions = generate_real_hotspots()
        
        return {
            "status": "success",
            "hotspots": predictions
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Required data files not found: {str(e)}"
        )
        
    except ValueError as e:
        logger.error(f"Model validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Model validation failed: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate predictions: {str(e)}"
        )

