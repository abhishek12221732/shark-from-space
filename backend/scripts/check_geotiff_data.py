#!/usr/bin/env python3
"""
Check what data is actually in the GeoTIFF files
"""

import rasterio
import numpy as np
from pathlib import Path

def check_geotiff_data():
    """Check the actual data values in the GeoTIFF files"""

    backend_dir = Path(__file__).resolve().parent.parent
    data_dir = backend_dir / "data" / "EarthEngine_Exports"

    chl_path = data_dir / "MODIS_Chlorophyll_2020_Mean.tif"
    sst_path = data_dir / "NOAA_Pathfinder_SST_2020_Mean.tif"

    print("Checking GeoTIFF data values...")

    # Test coordinates from the grid generation
    center_lat = -13.00
    center_lon = 46.23
    spacing = 0.02
    grid_size = 40

    # Generate a few sample coordinates
    sample_coords = []
    for i in range(5):  # First 5 points
        lat = center_lat + (i - grid_size/2 + 0.5) * spacing
        lon = center_lon + (i - grid_size/2 + 0.5) * spacing
        sample_coords.append((lon, lat))  # rasterio expects (x, y) = (lon, lat)

    print(f"Testing {len(sample_coords)} sample coordinates around center ({center_lat}, {center_lon})")

    try:
        # Open files
        with rasterio.open(chl_path) as chl_ds, rasterio.open(sst_path) as sst_ds:
            print(f"\nChlorophyll file bounds: {chl_ds.bounds}")
            print(f"SST file bounds: {sst_ds.bounds}")

            # Sample values
            chl_samples = list(chl_ds.sample(sample_coords))
            sst_samples = list(sst_ds.sample(sample_coords))

            print("\nSample data:")
            print("Coord (lon, lat) -> Chl value, SST value")

            for i, (coord, chl_sample, sst_sample) in enumerate(zip(sample_coords, chl_samples, sst_samples)):
                lon, lat = coord

                chl_val = chl_sample[0] if len(chl_sample) > 0 else None
                sst_val = sst_sample[0] if len(sst_sample) > 0 else None

                print(f"  {i+1}. ({lon:.4f}, {lat:.4f}) -> Chl: {chl_val}, SST: {sst_val}")

                # Check if values are valid
                chl_valid = (chl_val is not None and not np.isnan(chl_val) and
                           not (hasattr(chl_val, '__array__') and np.ma.is_masked(chl_val)))

                sst_valid = (sst_val is not None and not np.isnan(sst_val) and
                           not (hasattr(sst_val, '__array__') and np.ma.is_masked(sst_val)))

                if chl_valid and sst_valid:
                    print("    ✓ Valid data")
                else:
                    print("    ✗ Invalid data")

    except Exception as e:
        print(f"Error checking GeoTIFF data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_geotiff_data()