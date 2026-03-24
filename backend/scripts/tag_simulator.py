import time
import requests
import random
import math
import threading  # <--- Added threading
from datetime import datetime, timezone

# The API endpoint
API_ENDPOINT = "http://127.0.0.1:8000/events/ingest"

def simulate_tag(tag_id, start_lat, start_lon):
    """
    Simulates a single shark tag, sending data every few seconds.
    """
    lat, lon = start_lat, start_lon
    print(f"🦈 Starting simulation for tag: {tag_id}...")
    
    t = 0
    while True:
        t += 1
        
        # 1. Simulate movement (random walk)
        lat += (random.random() - 0.5) * 0.01
        lon += (random.random() - 0.5) * 0.01
        
        # 2. Simulate dive profile
        depth = abs(math.sin(t / 10.0)) * 200 + random.random() * 5
        
        # 3. Simulate event trigger
        event = "transiting"
        confidence = 0.5
        accel = [round(random.random(), 2) for _ in range(3)]
        
        # Occasional feeding event
        if random.random() < 0.1: # Increased chance for demo purposes
            event = "possible_feeding"
            confidence = 0.9
            print(f"*** {tag_id} triggered FEEDING EVENT ***")
        
        # 4. Construct payload
        payload = {
          "tag_id": tag_id,
          "timestamp": datetime.now(timezone.utc).isoformat(),
          "latitude": round(lat, 6),
          "longitude": round(lon, 6),
          "depth_m": round(depth, 2),
          "acceleration": accel,
          "env_temperature_c": round(24.5, 2),
          "salinity_psu": round(36.1, 2),
          "battery_level_pct": 80,
          "event_trigger": event,
          "event_confidence": confidence
        }

        # 5. Send data
        try:
            requests.post(API_ENDPOINT, json=payload)
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Connection Error for {tag_id}")
        
        # Random delay between 2-5 seconds for this shark
        time.sleep(random.randint(2, 5))

if __name__ == "__main__":
    # Define our sharks and their starting positions
    sharks = [
        ("SHK001", -13.00, 46.23), # Shark 1
        ("SHK002", -13.05, 46.20), # Shark 2
        ("SHK003", -12.95, 46.25)  # Shark 3
    ]

    threads = []
    for shark in sharks:
        # Create a separate thread for each shark
        t = threading.Thread(target=simulate_tag, args=shark)
        t.daemon = True # Kills threads when main program exits
        t.start()
        threads.append(t)

    # Keep the main script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping simulation...")