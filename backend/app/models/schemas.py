from pydantic import BaseModel
from typing import List

class TagPayload(BaseModel):
    tag_id: str
    timestamp: str
    latitude: float
    longitude: float
    depth_m: float
    acceleration: List[float]
    env_temperature_c: float
    salinity_psu: float
    battery_level_pct: int
    event_trigger: str
    event_confidence: float