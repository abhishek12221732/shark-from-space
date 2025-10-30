import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic_settings import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId # Import ObjectId
from pathlib import Path # <-- IMPORT PATHLIB

# --- Configuration ---

# DEFINE THE PATHS
# Get the directory where this main.py file is located
BASE_DIR = Path(__file__).resolve().parent 
# Define the full, absolute path to the .env file
ENV_FILE_PATH = BASE_DIR / ".env" 

# Uses pydantic-settings to read from the .env file
class Settings(BaseSettings):
    mongo_connection_string: str
    
    class Config:
        env_file = ENV_FILE_PATH # <-- USE THE ABSOLUTE PATH
        env_file_encoding = 'utf-8'

settings = Settings()

# --- MongoDB Connection ---
# This is done once when the app starts
try:
    client = AsyncIOMotorClient(settings.mongo_connection_string)
    db = client.shark_database # Get the database
    events_collection = db.get_collection("events") # Get the collection
    hotspots_collection = db.get_collection("hotspots") # <-- ADD THIS LINE
    print("Successfully connected to MongoDB Atlas.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None
# --- End of MongoDB Setup ---

app = FastAPI(title="Shark Foraging Project API")

# --- CORS Configuration ---
origins = [
    "http://localhost:3000", 
    "http://localhost", 
    "http://localhost:5173"  # <-- THE FIX IS HERE
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End of CORS Configuration ---


# --- Pydantic Models (Data Schema) ---
class TagPayload(BaseModel):
    tag_id: str
    timestamp: str # ISO format string
    latitude: float
    longitude: float
    depth_m: float
    acceleration: List[float]
    env_temperature_c: float
    salinity_psu: float
    battery_level_pct: int
    event_trigger: str
    event_confidence: float

# Helper to convert MongoDB's ObjectId to a string
def event_helper(event) -> dict:
    event["id"] = str(event["_id"]) # Create a new 'id' field with the string
    event["timestamp"] = event["timestamp"].isoformat() # Convert datetime to string
    event.pop("_id") # <-- THE FIX: Remove the original ObjectId field
    return event

# Helper for hotspot data
def hotspot_helper(hotspot) -> dict:
    hotspot["id"] = str(hotspot["_id"])
    hotspot.pop("_id")
    return hotspot

@app.post("/ingest_tag_event")
async def ingest_tag_event(payload: TagPayload):
    """
    Receives tag data and saves it to the MongoDB 'events' collection.
    """
    if client is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        data = payload.dict()
        # Convert timestamp string to a real datetime object for better sorting in Mongo
        data['timestamp'] = datetime.fromisoformat(payload.timestamp)
        
        new_event = await events_collection.insert_one(data)
        
        print(f"Received and stored data from {payload.tag_id} (Doc ID: {new_event.inserted_id})")
        
        return {"status": "success", "doc_id": str(new_event.inserted_id)}
        
    except Exception as e:
        print(f"Error storing data: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.get("/events")
async def get_events():
    """
    Fetches the 20 most recent events from MongoDB
    to display on the React dashboard.
    """
    if client is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        events = []
        # Find, sort by timestamp descending, limit to 20
        cursor = events_collection.find().sort("timestamp", -1).limit(20)
        
        async for event in cursor:
            events.append(event_helper(event))
            
        return {"status": "success", "events": events}
        
    except Exception as e:
        print(f"Error fetching events: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.get("/hotspots")
async def get_hotspots():
    """
    Fetches all prediction hotspot data from MongoDB.
    """
    if client is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        hotspots = []
        # Find all hotspots (no limit for now, as it's a small grid)
        cursor = hotspots_collection.find()
        
        async for hotspot in cursor:
            hotspots.append(hotspot_helper(hotspot))
            
        return {"status": "success", "hotspots": hotspots}
        
    except Exception as e:
        print(f"Error fetching hotspots: {e}")
        return {"status": "error", "message": str(e)}, 500

# This allows running the app directly with `python backend/main.py`
if __name__ == "__main__":
    print("Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["backend"])






