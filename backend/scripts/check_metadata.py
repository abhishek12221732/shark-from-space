#!/usr/bin/env python3
"""
Check GeoTIFF metadata to understand data scaling
"""

import rasterio
from pathlib import Path

def check_geotiff_metadata():
    """Check the metadata and scaling information in GeoTIFF files"""

    backend_dir = Path(__file__).resolve().parent.parent
    data_dir = backend_dir / "data" / "EarthEngine_Exports"

    chl_path = data_dir / "MODIS_Chlorophyll_2020_Mean.tif"
    sst_path = data_dir / "NOAA_Pathfinder_SST_2020_Mean.tif"

    print("Checking GeoTIFF metadata...")

    for name, path in [("Chlorophyll", chl_path), ("SST", sst_path)]:
        print(f"\n=== {name} ===")
        try:
            with rasterio.open(path) as ds:
                print(f"Driver: {ds.driver}")
                print(f"Data type: {ds.dtypes[0]}")
                print(f"No data value: {ds.nodata}")
                print(f"Scale: {ds.scales}")
                print(f"Offset: {ds.offsets}")
                print(f"Units: {ds.units}")
                print(f"CRS: {ds.crs}")
                print(f"Transform: {ds.transform}")

                # Check tags
                tags = ds.tags()
                if tags:
                    print(f"Tags: {tags}")

                # Check band tags
                band_tags = ds.tags(1)
                if band_tags:
                    print(f"Band 1 tags: {band_tags}")

                # Read a small sample
                data = ds.read(1, window=((0, 10), (0, 10)))
                print(f"Sample data shape: {data.shape}")
                print(f"Sample data range: {data.min():.6f} - {data.max():.6f}")
                print(f"Sample data mean: {data.mean():.6f}")

        except Exception as e:
            print(f"Error reading {name}: {e}")

if __name__ == "__main__":
    check_geotiff_metadata()