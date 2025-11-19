"""
Helper functions for data transformation.
"""

from typing import Dict, Any


def event_helper(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB event document to API-friendly format.
    
    Args:
        event: MongoDB document with _id and timestamp fields
        
    Returns:
        Dictionary with id (string) and timestamp (ISO string)
    """
    result = event.copy()
    result["id"] = str(result["_id"])
    result["timestamp"] = result["timestamp"].isoformat()
    result.pop("_id", None)
    return result


def hotspot_helper(hotspot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB hotspot document to API-friendly format.
    
    Args:
        hotspot: MongoDB document with _id field
        
    Returns:
        Dictionary with id (string) instead of _id
    """
    result = hotspot.copy()
    result["id"] = str(result["_id"])
    result.pop("_id", None)
    return result

