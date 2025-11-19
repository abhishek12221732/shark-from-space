import random
import time
import sys
from pathlib import Path
import asyncio

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.database import get_hotspots_collection

# --- MongoDB Connection ---
try:
    from app.core.database import get_database
    db = get_database()
    if db is None:
        raise Exception("Database connection failed")
    hotspots_collection = db.get_collection("hotspots")
    print("Successfully connected to MongoDB Atlas.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    hotspots_collection = None

async def generate_dummy_hotspots():
    """
    Generates a grid of dummy prediction data and saves to MongoDB.
    This simulates the output of the ML model.
    """
    if client is None:
        print("Database not connected. Exiting.")
        return

    print("Deleting old hotspot data...")
    await hotspots_collection.delete_many({})

    print("Generating new dummy hotspot grid...")
    hotspots = []
    
    # Base location from your report
    base_lat = -13.00
    base_lon = 46.23
    grid_size = 0.01 # The resolution of the map

    for i in range(20): # 20x20 grid
        for j in range(20):
            lat = base_lat + (i * grid_size) + (random.random() - 0.5) * 0.005
            lon = base_lon + (j * grid_size) + (random.random() - 0.5) * 0.005
            
            # Create a "hotspot" (high value) near the middle
            if 8 < i < 12 and 8 < j < 12:
                prediction_value = random.uniform(0.7, 1.0)
            else:
                prediction_value = random.uniform(0.1, 0.5)

            hotspot_data = {
                "latitude": lat,
                "longitude": lon,
                "prediction_value": prediction_value
            }
            hotspots.append(hotspot_data)

    if hotspots:
        await hotspots_collection.insert_many(hotspots)
        print(f"Successfully inserted {len(hotspots)} dummy hotspot points.")

if __name__ == "__main__":
    asyncio.run(generate_dummy_hotspots())
