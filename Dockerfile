FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for rasterio/GDAL, data download, and procps for process management)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root directory and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

# Copy scripts directory
COPY backend/scripts ./scripts

# Download real data files from GitHub release
RUN mkdir -p ./data/EarthEngine_Exports && \
    cd ./data/EarthEngine_Exports && \
    wget -q https://github.com/abhishek12221732/shark-from-space/releases/download/v1.0.0-data/MODIS_Chlorophyll_2020_Mean.tif && \
    wget -q https://github.com/abhishek12221732/shark-from-space/releases/download/v1.0.0-data/NOAA_Pathfinder_SST_2020_Mean.tif && \
    wget -q https://github.com/abhishek12221732/shark-from-space/releases/download/v1.0.0-data/Shark_Habitat_Suitability_2020.tif && \
    wget -q https://github.com/abhishek12221732/shark-from-space/releases/download/v1.0.0-data/shark_habitat_model.pkl && \
    cd /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "app.main:app"]
