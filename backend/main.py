# File: backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from fastapi.middleware.cors import CORSMiddleware  # Import CORS

app = FastAPI(title="Shark Foraging Project API")

# --- CORS Configuration ---
# This allows your React app (running on http://localhost:3000)
# to make requests to this API.
origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# --- End of CORS Configuration ---


# Define the data schema from Section 5: Data Schema
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

@app.get("/")
def read_root():
    # Simple test endpoint for React to hit
    return {"status": "Shark Foraging API is running."}

# This is the endpoint from Section 9: API Spec
@app.post("/ingest_tag_event")
async def ingest_tag_event(payload: TagPayload):
    # For now, we just print the received data
    # Later, you will store this in MongoDB/Firestore (Section 9)
    print(f"Received data from {payload.tag_id}: {payload.event_trigger}")
    
    return {"status": "success", "received_tag_id": payload.tag_id}