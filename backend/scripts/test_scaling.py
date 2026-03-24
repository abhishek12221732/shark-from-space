#!/usr/bin/env python3
"""
Test different scaling factors for SST data
"""

import sys
import joblib
import numpy as np
from pathlib import Path

def test_scaling_factors():
    """Test different scaling factors for SST data"""

    backend_dir = Path(__file__).resolve().parent.parent
    model_path = backend_dir / "data" / "EarthEngine_Exports" / "shark_habitat_model.pkl"

    print("Testing different SST scaling factors...")

    try:
        model = joblib.load(model_path)

        # Test SST values we observed: 2382-2393
        raw_sst = 2382.0
        chlorophyll = 0.14  # Typical value we saw

        print(f"Raw SST value: {raw_sst}")
        print(f"Chlorophyll value: {chlorophyll}")
        print()

        # Test different scaling factors
        scale_factors = [1, 10, 100, 1000, 273.15]  # Kelvin offset

        for scale in scale_factors:
            if scale == 273.15:
                scaled_sst = raw_sst - scale  # Convert from Kelvin to Celsius
                desc = "Convert from Kelvin to Celsius"
            else:
                scaled_sst = raw_sst / scale
                desc = f"Divide by {scale}"

            # Test prediction
            X = np.array([[chlorophyll, scaled_sst]], dtype=np.float32)
            prediction = model.predict(X)
            pred_value = float(prediction[0])

            print(f"  {desc}: SST={scaled_sst:.1f}°C -> Prediction={pred_value:.4f}")
        print()
        print("Expected SST range for ocean: 15-35°C")
        print("Expected prediction range: 0-1 (after clipping)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scaling_factors()