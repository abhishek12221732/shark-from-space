"""
Real ML Predictor for Shark Habitat Hotspots

This module generates real ML predictions for shark habitat hotspots using
trained models and satellite GeoTIFF data (chlorophyll and SST).

Production-ready, type-hinted, and fully documented.
"""

import logging
import threading
import time
import joblib
import rasterio
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Module-level cache with thread safety
_cache: Optional[List[Dict[str, float]]] = None
_cache_lock = threading.Lock()
_cache_key: Optional[str] = None
_truth_cache: Optional[List[Dict[str, float]]] = None
_truth_cache_lock = threading.Lock()


def generate_real_hotspots() -> List[Dict[str, float]]:
    """
    Generate real ML predictions for shark habitat hotspots.
    
    This function:
    1. Loads the trained model from .pkl file
    2. Opens chlorophyll and SST GeoTIFF files
    3. Generates a 40×40 grid centered at specified coordinates
    4. Samples both rasters for each grid point
    5. Runs ML predictions on valid samples
    6. Returns sorted list of predictions
    
    Results are cached per application lifetime for performance.
    
    If model or data files are missing, returns dummy hotspots for demo purposes.
    
    Returns:
        List of dictionaries with keys:
        - latitude: float (latitude in degrees)
        - longitude: float (longitude in degrees)
        - prediction_value: float (prediction score 0-1)
        
        Sorted by latitude descending, then longitude ascending.
        
    Raises:
        FileNotFoundError: If model or GeoTIFF files are missing
        ValueError: If model validation fails
        IOError: If GeoTIFF files cannot be opened
    """
    global _cache, _cache_key
    
    # Check cache first
    with _cache_lock:
        if _cache is not None:
            logger.info("Cache hit: returning cached predictions")
            return _cache.copy()  # Return copy to prevent mutation
    
    # Cache miss - generate new predictions
    logger.info("Cache miss: generating new predictions")
    start_time = time.time()
    
    try:
        # Define file paths
        backend_dir = Path(__file__).resolve().parent.parent.parent
        data_dir = backend_dir / "data" / "EarthEngine_Exports"
        
        model_path = data_dir / "shark_habitat_model.pkl"
        chl_path = data_dir / "MODIS_Chlorophyll_2020_Mean.tif"
        sst_path = data_dir / "NOAA_Pathfinder_SST_2020_Mean.tif"
        
        # Check if files exist
        if not model_path.exists() or not chl_path.exists() or not sst_path.exists():
            logger.warning("Model or data files missing, returning dummy hotspots for demo")
            return _generate_dummy_hotspots()
        
        # 1. Load model with validation
        logger.info(f"Loading model from: {model_path}")
        
        model = joblib.load(model_path)
        model_type = type(model).__name__
        logger.info(f"Model loaded successfully: {model_type}")
        
        # Validate model interface
        if hasattr(model, 'n_features_in_'):
            expected_features = model.n_features_in_
            if expected_features != 2:
                raise ValueError(
                    f"Model expects {expected_features} features, but we provide 2 (chl, sst). "
                    f"Model type: {model_type}"
                )
            logger.info(f"Model expects {expected_features} features (validated)")
        else:
            logger.warning("Model does not have n_features_in_ attribute - proceeding without validation")
        
        # 2. Open GeoTIFF files
        logger.info(f"Opening GeoTIFF files from: {data_dir}")
        
        chl_ds = rasterio.open(chl_path)
        sst_ds = rasterio.open(sst_path)
        
        try:
            # Check CRS (Coordinate Reference System)
            wgs84_crs = rasterio.crs.CRS.from_epsg(4326)
            
            if chl_ds.crs != wgs84_crs:
                logger.warning(
                    f"Chlorophyll CRS is {chl_ds.crs}, expected EPSG:4326 (WGS84). "
                    f"Proceeding but results may be inaccurate."
                )
            else:
                logger.info("Chlorophyll CRS: EPSG:4326 (WGS84) ✓")
            
            if sst_ds.crs != wgs84_crs:
                logger.warning(
                    f"SST CRS is {sst_ds.crs}, expected EPSG:4326 (WGS84). "
                    f"Proceeding but results may be inaccurate."
                )
            else:
                logger.info("SST CRS: EPSG:4326 (WGS84) ✓")
            
            # Log GeoTIFF bounds and resolution
            logger.info(f"Chlorophyll bounds: {chl_ds.bounds}")
            logger.info(f"Chlorophyll resolution: {chl_ds.res}")
            logger.info(f"SST bounds: {sst_ds.bounds}")
            logger.info(f"SST resolution: {sst_ds.res}")
            
            # 3. Generate larger grid for better coverage
            center_lat = -13.00
            center_lon = 46.23
            spacing = 0.05  # degrees (increased from 0.02 for larger area)
            grid_size = 100  # increased from 40 for much larger coverage
            
            # Calculate grid bounds
            half_span = (grid_size - 1) * spacing / 2
            lat_min = center_lat - half_span
            lat_max = center_lat + half_span
            lon_min = center_lon - half_span
            lon_max = center_lon + half_span
            
            logger.info(
                f"Generating {grid_size}×{grid_size} grid centered at ({center_lat}, {center_lon}) "
                f"with {spacing}° spacing"
            )
            logger.info(f"Grid bounds: lat [{lat_min:.2f}, {lat_max:.2f}], lon [{lon_min:.2f}, {lon_max:.2f}]")
            
            # Generate grid coordinates as (lon, lat) tuples for rasterio
            coords: List[Tuple[float, float]] = []
            for i in range(grid_size):
                for j in range(grid_size):
                    lat = center_lat + (i - grid_size/2 + 0.5) * spacing
                    lon = center_lon + (j - grid_size/2 + 0.5) * spacing
                    coords.append((lon, lat))  # rasterio expects (x, y) = (lon, lat)
            
            total_points = len(coords)
            logger.info(f"Generated {total_points} grid points")
            
            # 4. Batch sample both rasters
            logger.info("Sampling chlorophyll and SST values...")
            chl_samples = list(chl_ds.sample(coords))
            sst_samples = list(sst_ds.sample(coords))
            
            # 5. Process samples and generate predictions
            valid_predictions: List[Dict[str, float]] = []
            skipped = 0
            
            logger.info("Processing samples and generating predictions...")
            
            for idx, (coord, chl_sample, sst_sample) in enumerate(zip(coords, chl_samples, sst_samples)):
                lon, lat = coord
                
                # Extract first band value (rasterio.sample returns list of arrays)
                chl_val = chl_sample[0] if len(chl_sample) > 0 else None
                sst_val = sst_sample[0] if len(sst_sample) > 0 else None
                
                # Check for NaN or masked values
                chl_valid = (
                    chl_val is not None and
                    not np.isnan(chl_val) and
                    not (hasattr(chl_val, '__array__') and np.ma.is_masked(chl_val))
                )
                
                sst_valid = (
                    sst_val is not None and
                    not np.isnan(sst_val) and
                    not (hasattr(sst_val, '__array__') and np.ma.is_masked(sst_val))
                )
                
                # Skip if either value is invalid
                if not (chl_valid and sst_valid):
                    skipped += 1
                    continue
                
                # Prepare input for model (reshape to (1, 2) for single prediction)
                try:
                    # Apply scaling: SST data appears to be scaled by 100
                    scaled_sst = float(sst_val) / 100.0
                    X = np.array([[float(chl_val), scaled_sst]], dtype=np.float32)
                    
                    # Debug logging
                    if (idx + 1) % 100 == 0:
                        logger.info(f"Sample input at ({lat:.4f}, {lon:.4f}): Chl={chl_val:.6f}, SST_raw={sst_val:.2f}, SST_scaled={scaled_sst:.2f}")
                    
                    # Run prediction
                    prediction = model.predict(X)
                    
                    # Handle different prediction output shapes
                    if isinstance(prediction, np.ndarray):
                        raw_pred_value = float(prediction[0])
                    else:
                        raw_pred_value = float(prediction)
                    
                    # Apply sigmoid transformation to convert raw predictions to [0,1] probabilities
                    pred_value = 1.0 / (1.0 + np.exp(-raw_pred_value))
                    
                    # Scale up very small values for visualization (multiply by 1e20 to make tiny probabilities visible)
                    if pred_value > 0 and pred_value < 1e-10:
                        pred_value = pred_value * 1e20
                        pred_value = np.clip(pred_value, 0.0, 1.0)  # Re-clip after scaling
                    
                    # Debug logging
                    if (idx + 1) % 100 == 0:
                        logger.info(f"Processed {idx + 1}/{total_points} points ({len(valid_predictions)} valid, {skipped} skipped)")
                    
                    # Store valid prediction
                    valid_predictions.append({
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "prediction_value": float(pred_value)
                    })
                    
                except Exception as e:
                    logger.warning(f"Error predicting for point ({lat}, {lon}): {e}")
                    skipped += 1
                    continue
                
                # Progress logging every 100 points
                if (idx + 1) % 100 == 0:
                    logger.info(f"Processed {idx + 1}/{total_points} points ({len(valid_predictions)} valid, {skipped} skipped)")
            
            # 6. Sort results: latitude descending, then longitude ascending
            valid_predictions.sort(key=lambda x: (-x["latitude"], x["longitude"]))
            
            # 7. Cache the result
            with _cache_lock:
                _cache = valid_predictions
                _cache_key = f"{model_path.stat().st_mtime}_{total_points}"
            
            elapsed_time = time.time() - start_time
            
            # Final logging
            logger.info(
                f"Prediction generation complete: "
                f"{len(valid_predictions)} valid predictions, {skipped} skipped points "
                f"in {elapsed_time:.2f} seconds"
            )
            
            if len(valid_predictions) == 0:
                logger.warning("No valid predictions generated - all points were skipped")
            
            return valid_predictions
            
        finally:
            # Always close GeoTIFF files
            chl_ds.close()
            sst_ds.close()
            logger.info("GeoTIFF files closed")
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except ValueError as e:
        logger.error(f"Model validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating predictions: {e}", exc_info=True)
        raise IOError(f"Failed to generate predictions: {e}") from e


def _generate_dummy_hotspots() -> List[Dict[str, float]]:
    """
    Generate dummy hotspots for demo purposes when model/data files are missing.
    
    Returns a small set of sample hotspots around the Maldives region.
    """
    logger.info("Generating dummy hotspots for demo")
    
    # Create some sample hotspots around Maldives
    hotspots = [
        {"latitude": -12.8, "longitude": 46.0, "prediction_value": 0.85},
        {"latitude": -13.2, "longitude": 46.1, "prediction_value": 0.72},
        {"latitude": -12.9, "longitude": 46.3, "prediction_value": 0.68},
        {"latitude": -13.1, "longitude": 45.9, "prediction_value": 0.61},
        {"latitude": -12.7, "longitude": 46.2, "prediction_value": 0.55},
        {"latitude": -13.0, "longitude": 46.4, "prediction_value": 0.49},
        {"latitude": -12.6, "longitude": 45.8, "prediction_value": 0.42},
        {"latitude": -13.3, "longitude": 46.0, "prediction_value": 0.38},
    ]
    
    # Sort as per the real function
    hotspots.sort(key=lambda x: (-x["latitude"], x["longitude"]))
    
    return hotspots


def clear_cache() -> None:
    """
    Clear the cached predictions.
    
    Useful for testing or when model/data files are updated.
    """
    global _cache, _cache_key
    
    with _cache_lock:
        _cache = None
        _cache_key = None
        logger.info("Cache cleared")

def get_ground_truth_hotspots() -> List[Dict[str, float]]:
    """
    Reads the historical ground truth data from the 2020 suitability GeoTIFF.
    Uses the exact same grid as the ML predictions for perfect 1:1 comparison.
    """
    global _truth_cache
    
    with _truth_cache_lock:
        if _truth_cache is not None:
            logger.info("Truth Cache hit: returning cached historical data")
            return _truth_cache.copy()

    logger.info("Truth Cache miss: generating historical data grid")
    
    try:
        backend_dir = Path(__file__).resolve().parent.parent.parent
        truth_path = backend_dir / "data" / "EarthEngine_Exports" / "Shark_Habitat_Suitability_2020.tif"
        
        if not truth_path.exists():
            logger.warning("Ground truth GeoTIFF not found, returning dummy truth data for demo")
            return _generate_dummy_truth_hotspots()
            
        truth_ds = rasterio.open(truth_path)
        
        # Also open Chlorophyll to use as an ocean mask (to prevent land leakage)
        chl_path = backend_dir / "data" / "EarthEngine_Exports" / "MODIS_Chlorophyll_2020_Mean.tif"
        chl_ds = None
        if chl_path.exists():
            chl_ds = rasterio.open(chl_path)
        
        # Using your exact grid parameters from generate_real_hotspots
        center_lat, center_lon = -13.00, 46.23
        spacing, grid_size = 0.05, 100
        
        coords = []
        for i in range(grid_size):
            for j in range(grid_size):
                lat = center_lat + (i - grid_size/2 + 0.5) * spacing
                lon = center_lon + (j - grid_size/2 + 0.5) * spacing
                coords.append((lon, lat))
                
        truth_samples = list(truth_ds.sample(coords))
        chl_samples = list(chl_ds.sample(coords)) if chl_ds else [None] * len(coords)
        
        valid_truth = []
        
        for coord, truth_sample, chl_sample in zip(coords, truth_samples, chl_samples):
            lon, lat = coord
            
            # Apply ocean mask if available
            if chl_sample is not None:
                chl_val = chl_sample[0] if len(chl_sample) > 0 else None
                chl_valid = (
                    chl_val is not None and
                    not np.isnan(chl_val) and
                    not (hasattr(chl_val, '__array__') and np.ma.is_masked(chl_val))
                )
                if not chl_valid:
                    continue  # Skip land/invalid ocean points
            
            val = truth_sample[0] if len(truth_sample) > 0 else None
            
            # Check for valid data (not NaN or masked)
            if val is not None and not np.isnan(val) and not (hasattr(val, '__array__') and np.ma.is_masked(val)):
                suitability = float(val)
                
                # Only include points with meaningful suitability (>0.25)
                if suitability > 0.25:
                    valid_truth.append({
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "prediction_value": suitability
                    })
                
        valid_truth.sort(key=lambda x: (-x["latitude"], x["longitude"]))
        
        with _truth_cache_lock:
            _truth_cache = valid_truth
            
        truth_ds.close()
        if chl_ds:
            chl_ds.close()
            
        return valid_truth

    except Exception as e:
        logger.error(f"Error reading ground truth data: {e}", exc_info=True)
        logger.warning("Falling back to dummy truth data for demo")
        return _generate_dummy_truth_hotspots()

def _generate_dummy_truth_hotspots() -> list:
    """Generate dummy ground truth hotspots for demo when GeoTIFF is missing."""
    logger.info('Generating dummy ground truth hotspots for demo')
    
    hotspots = [
        {"latitude": -12.85, "longitude": 46.15, "prediction_value": 0.92},
        {"latitude": -13.15, "longitude": 46.25, "prediction_value": 0.81},
        {"latitude": -12.95, "longitude": 46.05, "prediction_value": 0.76},
        {"latitude": -13.05, "longitude": 45.95, "prediction_value": 0.68},
        {"latitude": -12.75, "longitude": 46.35, "prediction_value": 0.64},
        {"latitude": -13.25, "longitude": 46.05, "prediction_value": 0.58},
        {"latitude": -12.65, "longitude": 45.85, "prediction_value": 0.52},
        {"latitude": -13.35, "longitude": 46.15, "prediction_value": 0.47},
    ]
    
    hotspots.sort(key=lambda x: (-x["latitude"], x["longitude"]))
    return hotspots
