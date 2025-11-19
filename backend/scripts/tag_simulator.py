import time
import requests
import random
import math
import json
from datetime import datetime, timezone

# The API endpoint
API_ENDPOINT = "http://127.0.0.1:8000/events/ingest"

def simulate_tag(tag_id, start_lat, start_lon):
    """
    Simulates a single shark tag, sending data every few seconds.
    Based on Section 6 (Prototype Plan) and Section 5 (Data Schema).
    """
    lat, lon = start_lat, start_lon
    print(f"Starting simulation for tag: {tag_id}...")
    
    t = 0
    while True:
        t += 1
        
        # 1. Simulate movement (random walk)
        lat += (random.random() - 0.5) * 0.01
        lon += (random.random() - 0.5) * 0.01
        
        # 2. Simulate dive profile (sine wave)
        depth = abs(math.sin(t / 10.0)) * 200 + random.random() * 5 # Base dive + noise
        
        # 3. Simulate event trigger (from Section 8)
        event = "transiting"
        confidence = 0.5
        accel = [
            round(random.random() * 0.2, 3), 
            round(random.random() * 0.2, 3), 
            round(random.random() * 0.2, 3)
        ]
        
        # 2% chance of a feeding event
        if random.random() < 0.02:
            event = "possible_feeding"
            confidence = round(0.8 + random.random() * 0.1, 2)
            # Simulate high-acceleration event (Section 8)
            accel = [
                round(random.random() * 2, 3), 
                round(random.random() * 2, 3), 
                round(random.random() * 1.5, 3)
            ]
            print(f"*** {tag_id} triggered FEEDING EVENT ***")
        
        # 4. Construct payload (matches TagPayload in main.py)
        payload = {
          "tag_id": tag_id,
          "timestamp": datetime.now(timezone.utc).isoformat(),
          "latitude": round(lat, 6),
          "longitude": round(lon, 6),
          "depth_m": round(depth, 2),
          "acceleration": accel,
          "env_temperature_c": round(24.5 + (random.random() - 0.5), 2),
          "salinity_psu": round(36.1 + (random.random() - 0.1), 2),
          "battery_level_pct": 82, # Static for now
          "event_trigger": event,
          "event_confidence": confidence
        }

        # 5. Send data to API
        try:
            response = requests.post(API_ENDPOINT, json=payload)
            if response.status_code == 200:
                print(f"Sent {tag_id} data: {event}")
            else:
                print(f"Error sending data: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Is the backend server (main.py) running?")
            time.sleep(5) # Wait before retrying
        
        # Wait for a random time before next transmission
        time.sleep(random.randint(3, 7))

if __name__ == "__main__":
    # You can run multiple simulators by starting this script in multiple terminals
    # For now, we'll just run one.
    simulate_tag("SHK001", -13.004, 46.237)
