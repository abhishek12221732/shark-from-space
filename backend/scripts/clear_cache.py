#!/usr/bin/env python3
"""
Clear the ML prediction cache to force regeneration
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.ml_predictor import clear_cache

if __name__ == "__main__":
    print("Clearing ML prediction cache...")
    clear_cache()
    print("Cache cleared! Next request will regenerate predictions.")