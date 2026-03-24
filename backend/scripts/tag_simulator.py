import time
import requests
import random
import math
import threading
from datetime import datetime, timezone

# The API endpoints
INGEST_ENDPOINT = "http://127.0.0.1:8000/events/ingest"
HOTSPOTS_ENDPOINT = "http://127.0.0.1:8000/hotspots/real"

def simulate_tag(tag_id, start_lat, start_lon):
    """
    Simulates a single shark tag, sending data every few seconds.
    """
    lat, lon = start_lat, start_lon
    print(f"🦈 Starting simulation for {tag_id} at [{lat:.4f}, {lon:.4f}]...")
    
    t = 0
    while True:
        t += 1
        
        # 1. Simulate movement (random walk - slightly tightened to keep them in the hotspot)
        lat += (random.random() - 0.5) * 0.005
        lon += (random.random() - 0.5) * 0.005
        
        # 2. Simulate dive profile
        depth = abs(math.sin(t / 10.0)) * 200 + random.random() * 5
        
        # 3. Simulate event trigger
        event = "transiting"
        confidence = 0.5
        accel = [round(random.random(), 2) for _ in range(3)]
        
        # Occasional feeding event (10% chance)
        if random.random() < 0.1:
            event = "possible_feeding"
            confidence = 0.9 + (random.random() * 0.09) # 90-99% confidence
            print(f"*** {tag_id} triggered FEEDING EVENT ***")
        
        # 4. Construct payload
        payload = {
          "tag_id": tag_id,
          "timestamp": datetime.now(timezone.utc).isoformat(),
          "latitude": round(lat, 6),
          "longitude": round(lon, 6),
          "depth_m": round(depth, 2),
          "acceleration": accel,
          "env_temperature_c": round(24.5 + (random.random() * 2), 2),
          "salinity_psu": round(36.1, 2),
          "battery_level_pct": max(10, 100 - (t // 10)), # Slowly drain battery
          "event_trigger": event,
          "event_confidence": round(confidence, 2)
        }

        # 5. Send data
        try:
            requests.post(INGEST_ENDPOINT, json=payload)
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Connection Error for {tag_id}")
        
        # Random delay between 2-5 seconds for this shark
        time.sleep(random.randint(2, 5))

def get_smart_spawn_points(num_sharks=3):
    """
    Queries the ML backend for the highest probability hotspots,
    calculates the center of mass of the top 5% to find the visually
    densest region, and returns clustered coordinates.
    """
    print("🧠 Querying ML Model for optimal habitat density...")
    try:
        # Give the backend a second to ensure it's fully up
        time.sleep(1)
        response = requests.get(HOTSPOTS_ENDPOINT)
        
        if response.status_code == 200:
            data = response.json()
            hotspots = data.get("hotspots", [])
            
            if hotspots:
                # 1. Sort by highest prediction value
                sorted_spots = sorted(hotspots, key=lambda x: x["prediction_value"], reverse=True)
                
                # 2. Take the top 5% of points (the densest "hottest" zone)
                top_tier_count = max(10, len(hotspots) // 20)
                top_spots = sorted_spots[:top_tier_count]
                
                # 3. Calculate the "Center of Mass" of these top points
                avg_lat = sum(spot["latitude"] for spot in top_spots) / len(top_spots)
                avg_lon = sum(spot["longitude"] for spot in top_spots) / len(top_spots)
                
                print(f"📍 Visual Center of Mass found at [{avg_lat:.4f}, {avg_lon:.4f}]")
                
                spawns = []
                # 4. Spawn sharks clustered around this center of mass
                for i in range(num_sharks):
                    # Add a tiny random offset so they don't spawn exactly on the identical pixel
                    offset_lat = avg_lat + (random.random() - 0.5) * 0.03
                    offset_lon = avg_lon + (random.random() - 0.5) * 0.03
                    spawns.append((f"SHK00{i+1}", offset_lat, offset_lon))
                
                print(f"✅ Successfully clustered {num_sharks} sharks in the highest density zone!")
                return spawns
                
    except Exception as e:
        print(f"⚠️ Could not fetch smart spawn points: {e}")
        
    # Fallback coordinates if the API is unreachable
    print("⚠️ Falling back to default spawn points.")
    return [
        ("SHK001", -12.92, 46.18),
        ("SHK002", -12.95, 46.15),
        ("SHK003", -12.90, 46.20)
    ]

if __name__ == "__main__":
    print("--- SHARK FORAGING IoT SIMULATOR ---")
    
    # Dynamically grab the best starting positions
    sharks = get_smart_spawn_points(3)

    threads = []
    for shark in sharks:
        t = threading.Thread(target=simulate_tag, args=shark)
        t.daemon = True
        t.start()
        threads.append(t)

    # Keep the main script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping simulation...")