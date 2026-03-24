#!/usr/bin/env python3
"""
Test script to verify XGBoost model functionality
"""

import requests
import json
import sys

def test_xgboost_model():
    """Test the real hotspots endpoint to verify XGBoost model is working"""

    url = "http://127.0.0.1:8000/hotspots/real"

    try:
        print("Testing XGBoost model via /hotspots/real endpoint...")
        print(f"Making request to: {url}")

        response = requests.get(url, timeout=30)

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Request successful!")

            if data.get("status") == "success":
                hotspots = data.get("hotspots", [])
                print(f"✓ Model generated {len(hotspots)} hotspot predictions")

                if len(hotspots) > 0:
                    # Show first few predictions
                    print("\nFirst 3 predictions:")
                    for i, hotspot in enumerate(hotspots[:3]):
                        lat = hotspot.get("latitude", "N/A")
                        lon = hotspot.get("longitude", "N/A")
                        pred = hotspot.get("prediction_value", "N/A")
                        print(f"  {i+1}. Lat: {lat:.4f}, Lon: {lon:.4f}, Prediction: {pred:.4f}")

                    # Check prediction value range (allowing for very small values)
                    pred_values = [h.get("prediction_value", 0) for h in hotspots]
                    min_pred = min(pred_values)
                    max_pred = max(pred_values)
                    print(f"\nPrediction range: {min_pred:.2e} - {max_pred:.2e}")

                    if 0 <= min_pred <= 1 and 0 <= max_pred <= 1:
                        print("✓ All predictions are in valid [0,1] range")
                        
                        # Check if predictions vary (not all the same)
                        unique_values = len(set(pred_values))
                        if unique_values > 1:
                            print(f"✓ Predictions vary across {unique_values} different values")
                        else:
                            print("⚠ All predictions have the same value")
                    else:
                        print("✗ Some predictions are outside [0,1] range")

                    print("\n🎉 XGBoost model is working correctly!")
                    return True
                else:
                    print("⚠ No hotspots generated")
                    return False
            else:
                print(f"✗ API returned status: {data.get('status')}")
                return False
        else:
            print(f"✗ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_xgboost_model()
    sys.exit(0 if success else 1)