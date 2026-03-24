#!/usr/bin/env python3
"""
Direct test of the XGBoost model to understand why predictions are all zeros
"""

import sys
import joblib
import numpy as np
from pathlib import Path

def test_model_directly():
    """Test the XGBoost model directly with sample data"""

    # Path to model
    backend_dir = Path(__file__).resolve().parent.parent
    model_path = backend_dir / "data" / "EarthEngine_Exports" / "shark_habitat_model.pkl"

    print(f"Loading model from: {model_path}")

    try:
        # Load model
        model = joblib.load(model_path)
        print(f"✓ Model loaded: {type(model).__name__}")

        # Check model attributes
        if hasattr(model, 'n_features_in_'):
            print(f"✓ Model expects {model.n_features_in_} features")

        if hasattr(model, 'feature_names_in_'):
            print(f"✓ Feature names: {model.feature_names_in_}")

        # Test with different input values
        test_inputs = [
            [0.1, 25.0],    # Low chlorophyll, moderate SST
            [1.0, 25.0],    # Moderate chlorophyll, moderate SST
            [5.0, 25.0],    # High chlorophyll, moderate SST
            [1.0, 20.0],    # Moderate chlorophyll, cool SST
            [1.0, 30.0],    # Moderate chlorophyll, warm SST
            [10.0, 28.0],   # Very high chlorophyll, warm SST
        ]

        print("\nTesting model with sample inputs:")
        print("Format: [chlorophyll, SST] -> prediction")

        for i, input_data in enumerate(test_inputs):
            X = np.array([input_data], dtype=np.float32)
            prediction = model.predict(X)

            if isinstance(prediction, np.ndarray):
                pred_value = float(prediction[0])
            else:
                pred_value = float(prediction)

            print(f"  Test {i+1}: {input_data} -> {pred_value:.4f}")

        # Test with zeros
        X_zero = np.array([[0.0, 0.0]], dtype=np.float32)
        pred_zero = model.predict(X_zero)
        print(f"  Zero input: [0.0, 0.0] -> {float(pred_zero[0]):.4f}")

        print("\n✓ Model testing complete")

    except Exception as e:
        print(f"✗ Error testing model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_directly()