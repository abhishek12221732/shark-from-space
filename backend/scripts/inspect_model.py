#!/usr/bin/env python3
"""
Check if the XGBoost model has any preprocessing/scaling information
"""

import sys
import joblib
import numpy as np
from pathlib import Path

def inspect_model():
    """Inspect the XGBoost model for preprocessing information"""

    backend_dir = Path(__file__).resolve().parent.parent
    model_path = backend_dir / "data" / "EarthEngine_Exports" / "shark_habitat_model.pkl"

    print("Inspecting XGBoost model...")

    try:
        model = joblib.load(model_path)
        print(f"✓ Model type: {type(model).__name__}")

        # Check all attributes
        print("\nModel attributes:")
        for attr in dir(model):
            if not attr.startswith('_'):
                try:
                    value = getattr(model, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except:
                    print(f"  {attr}: <cannot access>")

        # Check if it's a pipeline
        if hasattr(model, 'steps'):
            print(f"\nModel is a pipeline with steps: {model.steps}")
            for step_name, step in model.steps:
                print(f"  {step_name}: {type(step).__name__}")
                if hasattr(step, 'scale_'):
                    print(f"    scale_: {step.scale_}")
                if hasattr(step, 'mean_'):
                    print(f"    mean_: {step.mean_}")
                if hasattr(step, 'var_'):
                    print(f"    var_: {step.var_}")

        # Check booster if it's an XGB model
        if hasattr(model, 'get_booster'):
            booster = model.get_booster()
            print(f"\nBooster attributes: {dir(booster)}")

    except Exception as e:
        print(f"Error inspecting model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_model()