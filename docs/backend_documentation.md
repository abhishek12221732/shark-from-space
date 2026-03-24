## Backend Documentation

### Overview
The backend is a FastAPI-based REST API for a Shark Foraging Prediction System. It handles real-time IoT tag telemetry ingestion, stores data in MongoDB Atlas, and provides ML-based habitat prediction endpoints using satellite ocean data (MODIS Chlorophyll and NOAA Pathfinder SST).

### Architecture
- **Framework**: FastAPI (async Python web framework)
- **Database**: MongoDB Atlas (via Motor async driver)
- **ML**: XGBoost model for habitat prediction
- **Data Sources**: GeoTIFF satellite imagery, IoT tag telemetry
- **Configuration**: Pydantic settings with environment variables

### Project Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py        # API router setup
│   │   └── endpoints/
│   │       ├── events.py      # Tag event endpoints
│   │       └── hotspots.py    # Prediction endpoints
│   ├── core/
│   │   ├── config.py          # Settings & configuration
│   │   ├── database.py        # MongoDB connection
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py         # Pydantic data models
│   │   └── __init__.py
│   ├── services/
│   │   ├── ml_predictor.py    # ML prediction service
│   │   └── __init__.py
│   └── utils/
│       ├── helpers.py         # Data transformation helpers
│       └── __init__.py
├── data/
│   └── EarthEngine_Exports/    # ML model & satellite data
│       ├── shark_habitat_model.pkl
│       ├── MODIS_Chlorophyll_2020_Mean.tif
│       ├── NOAA_Pathfinder_SST_2020_Mean.tif
│       └── Shark_Habitat_Suitability_2020.tif
└── scripts/
    ├── tag_simulator.py        # IoT tag data simulator
    └── ml_model_simulator.py   # Dummy hotspot generator
```

### Dependencies (requirements.txt)
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `pydantic>=2.0.0` - Data validation
- `pydantic-settings>=2.0.0` - Configuration
- `motor>=3.3.0` - Async MongoDB driver
- `requests>=2.31.0` - HTTP client
- `rasterio>=1.3.0` - GeoTIFF processing
- `joblib>=1.3.0` - Model serialization
- `numpy>=1.24.0` - Numerical computing

### Configuration (app/core/config.py)
- Loads settings from environment variables and `.env` file
- MongoDB connection string required
- API metadata (title, version, host, port)
- CORS origins for frontend access
- Uses Pydantic BaseSettings for validation

### Database Layer (app/core/database.py)
- Async MongoDB connection using Motor
- Global client and database instances
- Separate collections: `events` and `hotspots`
- Connection pooling and error handling
- Graceful shutdown cleanup

### Data Models (app/models/schemas.py)
- `TagPayload`: Pydantic model for IoT tag telemetry
  - Fields: tag_id, timestamp, latitude, longitude, depth_m, acceleration[], env_temperature_c, salinity_psu, battery_level_pct, event_trigger, event_confidence

### API Endpoints

#### Main App (app/main.py)
- **GET /**: API status and database connection check
- **GET /health**: Health check endpoint
- Startup/shutdown event handlers for database initialization
- CORS middleware configured
- API docs at `/docs` and `/redoc`

#### Events Endpoints (app/api/endpoints/events.py)
- **POST /api/v1/events/ingest**: Ingest tag telemetry data
  - Accepts TagPayload JSON
  - Converts timestamp to datetime
  - Stores in MongoDB events collection
  - Returns success with document ID
- **GET /api/v1/events**: Retrieve recent events
  - Query parameter: limit (default 20)
  - Returns events sorted by timestamp descending
  - Uses helper to format MongoDB documents

#### Hotspots Endpoints (app/api/endpoints/hotspots.py)
- **GET /api/v1/hotspots**: Get simulated hotspots from database
  - Returns stored dummy predictions
- **GET /api/v1/hotspots/real**: Generate real ML predictions
  - Uses XGBoost model with satellite data
  - 40×40 grid centered at (-13.00, 46.23)
  - Returns latitude, longitude, prediction_value
  - Thread-safe caching for performance

### ML Prediction Service (app/services/ml_predictor.py)
- `generate_real_hotspots()`: Core prediction function
  - Loads trained XGBoost model from pickle file
  - Opens MODIS Chlorophyll and NOAA SST GeoTIFFs
  - Validates CRS (expects EPSG:4326 WGS84)
  - Generates 40×40 grid (1600 points) with 0.02° spacing
  - Samples raster values at each grid point
  - Runs ML predictions, clips to [0,1] range
  - Sorts results by latitude desc, longitude asc
  - Thread-safe caching with file modification time tracking
- `clear_cache()`: Manual cache invalidation
- Comprehensive error handling and logging
- Performance: ~100 points processed per second

### Utilities (app/utils/helpers.py)
- `event_helper()`: Convert MongoDB event docs to API format
  - Converts _id to id string
  - Converts timestamp to ISO string
- `hotspot_helper()`: Convert MongoDB hotspot docs to API format
  - Converts _id to id string

### Scripts

#### Tag Simulator (backend/scripts/tag_simulator.py)
- Multi-threaded IoT tag simulation
- 3 sharks with random walk movement
- Sends telemetry every 2-5 seconds to `/events/ingest`
- Simulates depth profiles, acceleration, environmental data
- Occasional "feeding" events with high confidence
- Runs indefinitely until interrupted

#### ML Model Simulator (backend/scripts/ml_model_simulator.py)
- Generates dummy hotspot data for testing
- 20×20 grid around base location
- Higher prediction values in center region
- Inserts into MongoDB hotspots collection
- Used when real ML predictions unavailable

### Data Files
- **shark_habitat_model.pkl**: Trained XGBoost model
- **MODIS_Chlorophyll_2020_Mean.tif**: Satellite chlorophyll data
- **NOAA_Pathfinder_SST_2020_Mean.tif**: Sea surface temperature data
- **Shark_Habitat_Suitability_2020.tif**: Ground truth habitat data

### Error Handling
- Database connection failures return 500 with details
- File not found errors for ML data
- Model validation errors
- Input validation via Pydantic
- Comprehensive logging throughout

### Security Considerations
- No authentication implemented
- CORS configured for development origins
- MongoDB connection string in environment
- No input sanitization beyond Pydantic validation

### Performance
- Async database operations
- ML prediction caching
- Efficient GeoTIFF sampling
- Connection pooling

### Development Setup
- Requires Python 3.8+, MongoDB Atlas account
- Environment file: `backend/.env` with MongoDB connection
- Run: `python -m app.main` (starts uvicorn on 127.0.0.1:8000)

## Project Progress Assessment

### Current Status: **Prototype/Demo Level** (60-70% Complete)

#### Completed Features:
- ✅ Full FastAPI backend with async endpoints
- ✅ MongoDB Atlas integration
- ✅ Real ML prediction pipeline with satellite data
- ✅ IoT tag telemetry ingestion and storage
- ✅ Data simulators for development/testing
- ✅ Basic frontend with React/Leaflet map
- ✅ API documentation (Swagger/ReDoc)
- ✅ Docker-ready structure
- ✅ Jupyter notebooks for data processing pipeline

#### Missing/Incomplete:
- ❌ Unit tests and integration tests
- ❌ Authentication and authorization
- ❌ Input validation beyond basic Pydantic
- ❌ Error monitoring and logging aggregation
- ❌ API rate limiting
- ❌ Data backup and recovery
- ❌ Production deployment configuration
- ❌ CI/CD pipeline
- ❌ API versioning strategy
- ❌ Database migrations
- ❌ Performance monitoring
- ❌ Security hardening (HTTPS, secrets management)

#### Development Stage:
- Core functionality working
- Suitable for demos and proof-of-concept
- Requires significant work for production deployment
- ML model trained and integrated
- Data pipeline established but basic

#### Recommendations for Production:
1. Add comprehensive test suite
2. Implement authentication (JWT/OAuth)
3. Add monitoring (Prometheus/Grafana)
4. Security audit and hardening
5. Database optimization and indexing
6. API documentation improvements
7. Error handling standardization
8. Performance benchmarking

The project demonstrates strong technical foundation with modern async Python stack, but needs enterprise-grade features for production use.