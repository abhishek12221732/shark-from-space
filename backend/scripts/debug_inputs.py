#!/usr/bin/env python3
"""
Debug what values are actually being fed to the model
"""

import sys
import requests
import json
from pathlib import Path

def debug_model_inputs():
    """Check what values are being processed by the model"""

    # Add backend to path
    backend_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(backend_dir))

    from app.services.ml_predictor import generate_real_hotspots

    print("Debugging model inputs...")

    try:
        # This will show the detailed logging from ml_predictor.py
        predictions = generate_real_hotspots()

        print(f"\nGenerated {len(predictions)} predictions")

        if len(predictions) > 0:
            # Show first few predictions
            for i, pred in enumerate(predictions[:5]):
                print(f"  {i+1}. Lat: {pred['latitude']:.4f}, Lon: {pred['longitude']:.4f}, Pred: {pred['prediction_value']:.4f}")

            # Check prediction distribution
            pred_values = [p['prediction_value'] for p in predictions]
            unique_preds = set(pred_values)
            print(f"\nUnique prediction values: {sorted(unique_preds)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_model_inputs()