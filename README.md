# Shark Foraging Prediction System

AI-powered system for predicting shark habitat suitability using satellite ocean data (SST, chlorophyll) and real-time IoT tag tracking.

## Team

- Abhishek Kumar
- Abdul Kadir
- Rajdeep Ghosh
- Mansi Kumari
- Sania

## Tech Stack

**Backend:** FastAPI, MongoDB, Python  
**Frontend:** React, Vite, Leaflet  
**ML:** XGBoost, scikit-learn  
**Data:** MODIS Chlorophyll, NOAA Pathfinder SST

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)

### Installation

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### Configuration

Create `backend/.env`:

```env
mongo_connection_string=mongodb+srv://username:password@cluster.mongodb.net/
```

### Run Application

```bash
# Terminal 1: Start backend
cd backend
python -m app.main

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Access:
- Frontend: http://localhost:5173
- API Docs: http://127.0.0.1:8000/docs

## Project Structure

```
shark-from-space/
├── backend/
│   ├── app/              # FastAPI application
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration & database
│   │   ├── models/      # Pydantic schemas
│   │   ├── services/    # Business logic (ML predictor)
│   │   └── utils/       # Helper functions
│   ├── data/            # ML model & GeoTIFF files
│   └── scripts/         # Utility scripts
│
└── frontend/
    └── src/             # React application
```

## API Endpoints

- `GET /` - API status
- `GET /events` - Recent tag events
- `POST /events/ingest` - Ingest tag telemetry
- `GET /hotspots` - Simulated predictions
- `GET /hotspots/real` - Real ML predictions

## Features

- Real-time tag event tracking
- ML-based habitat prediction (40×40 grid)
- Interactive map visualization with heatmap
- Automatic fallback to real predictions if simulated unavailable

## Development

### Backend

```bash
cd backend
python -m app.main
```

### Frontend

```bash
cd frontend
npm run dev
```

### Scripts

```bash
# Simulate tag data
python backend/scripts/tag_simulator.py

# Generate dummy hotspots
python backend/scripts/ml_model_simulator.py
```

## License

See LICENSE file.
