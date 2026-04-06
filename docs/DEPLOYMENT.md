# Free Deployment Guide - Render + Vercel/Netlify

## Free Tier Options

| Service | Backend | Frontend | Free Tier | Downside |
|---------|---------|----------|-----------|----------|
| **Render** | ✅ | ❌ | Yes | Spins down after 15 mins inactivity |
| **Railway** | ✅ | ✅ | Yes ($5/month credit) | Limited usage |
| **Vercel** | ❌ | ✅ | Yes | No backend |
| **Netlify** | ❌ | ✅ | Yes | No backend |
| **PythonAnywhere** | ✅ | ❌ | Limited | Python only, restrictive |

## Recommended: Render (Backend) + Vercel (Frontend)

**Total Cost: $0/month** ✅

---

## Step 1: Prepare Backend for Deployment

### 1.1 Create `Dockerfile` in backend directory

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for rasterio/GDAL)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "app.main:app"]
```

### 1.2 Update `requirements.txt`

Add these lines to your `backend/requirements.txt`:
```
gunicorn>=21.0.0
python-dotenv>=1.0.0
```

### 1.3 Create `.dockerignore` in backend directory

```
__pycache__
*.pyc
.env
.git
.gitignore
.venv
venv/
```

### 1.4 Create `render.yaml` in project root

```yaml
services:
  - type: web
    name: shark-api
    env: python
    plan: free
    buildCommand: "pip install --upgrade pip && pip install -r backend/requirements.txt gunicorn"
    startCommand: "gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 backend.app.main:app"
    envVars:
      - key: MONGO_CONNECTION_STRING
        scope: run
        value: ${MONGO_CONNECTION_STRING}
```

---

## Step 2: Deploy Backend on Render

### 2.1 Push code to GitHub

```bash
git add .
git commit -m "Add deployment files"
git push origin main
```

### 2.2 Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Click "New +" → "Web Service"
4. Select your GitHub repository
5. Fill in the form:
   - **Name:** shark-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt && pip install gunicorn`
   - **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 backend.app.main:app`
   - **Plan:** Free

### 2.3 Add Environment Variables

In Render dashboard:
1. Go to your service → "Environment"
2. Add variable:
   - **Key:** `MONGO_CONNECTION_STRING`
   - **Value:** Your MongoDB Atlas connection string from `.env`

### 2.4 Deploy

Click "Create Web Service" and wait for deployment (2-3 minutes)

**Your backend URL will be:** `https://shark-api-xxxxx.onrender.com`

⚠️ **Important:** On free tier, the service will spin down after 15 minutes of inactivity. First request after sleep takes 30 seconds. To keep it alive, add uptime monitoring:

```python
# Create a GitHub Action that pings every 10 minutes
# Add .github/workflows/uptime-monitor.yml
```

---

## Step 3: Update Frontend API URL

### 3.1 Create `.env.production` in frontend directory

```env
VITE_API_URL=https://shark-api-xxxxx.onrender.com
```

### 3.2 Update `frontend/src/App.jsx`

Replace all hardcoded `http://127.0.0.1:8000` with:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Then use it in all fetch calls:
fetch(`${API_URL}/events?limit=200`)
```

Full example:
```javascript
// Change from:
fetch('http://127.0.0.1:8000/events?limit=200')

// To:
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
fetch(`${API_URL}/events?limit=200`)
```

---

## Step 4: Deploy Frontend on Vercel

### 4.1 Create `vercel.json` in project root

```json
{
  "projects": [
    {
      "name": "shark-foraging-frontend",
      "path": "frontend"
    }
  ],
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist"
}
```

### 4.2 Push to GitHub

```bash
git add .
git commit -m "Add frontend environment variables"
git push origin main
```

### 4.3 Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Add New Project"
4. Select your repository
5. **Import Settings:**
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

6. **Environment Variables:**
   - `VITE_API_URL`: `https://shark-api-xxxxx.onrender.com`

7. Click "Deploy"

**Your frontend URL will be:** `https://shark-foraging-xxxxx.vercel.app`

---

## Alternative: Deploy Entire Project on Railway

Railway also has a free tier ($5 credit/month, usually lasts 2-3 months):

### Step 1: Create `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile",
    "dockerfile": "backend/Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT backend.app.main:app"
  }
}
```

### Step 2: Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project
4. Select "Deploy from GitHub repo"
5. Add environment variables
6. Deploy

**Cost:** Free ($5/month credit good for ~2-3 months for small app)

---

## Step 5: Keep Backend Awake (Anti-Spin-down)

Create `.github/workflows/keep-alive.yml`:

```yaml
name: Keep Render API Awake

on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes

jobs:
  wake:
    runs-on: ubuntu-latest
    steps:
      - name: Ping API
        run: curl -f https://shark-api-xxxxx.onrender.com/ || exit 0
```

---

## Step 6: Test Deployment

1. **Frontend:** Open `https://shark-foraging-xxxxx.vercel.app`
2. **Backend API Docs:** Open `https://shark-api-xxxxx.onrender.com/docs`
3. **Check connection:** Look for "System Operational" status in frontend

---

## Troubleshooting

### Frontend can't connect to backend

**Error:** `Failed to load resource: the server responded with a status of 405`

**Solution:**
1. Check CORS in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shark-foraging-xxxxx.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Check environment variable in Render dashboard

### Backend throws 503 after 15 minutes

**Expected behavior** on free tier - service spins down. Keep the "Keep Alive" workflow running.

### MongoDB connection fails

**Check:**
1. Connection string is correct in Render environment variables
2. MongoDB Atlas IP whitelist includes Render IPs: `0.0.0.0/0` (or get Render's IP and whitelist it)

---

## Limitations of Free Tier

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| Spins down after 15 mins | 30s startup delay | Run uptime monitor |
| 1 instance only | No redundancy | None (upgrade plan) |
| Limited CPU/Memory | Slow ML predictions | Used cached results |
| No custom domain | Long URL | Upgrade Vercel ($7... |
| 512MB RAM | Might OOM with large GeoTIFFs | None (upgrade) |

---

## Cost Breakdown

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Render** | ✅ Free | Spins down after 15 mins |
| **Vercel** | ✅ Free | Unlimited deployments |
| **MongoDB Atlas** | ✅ Free (M0) | 512MB storage |
| **GitHub** | ✅ Free | Unlimited repos |
| **Total** | **$0/month** | Production-ready |

---

## Upgrade Path (When You Need Scale)

| to Paid | Render | Vercel | MongoDB |
|--------|--------|--------|---------|
| No spin-down | $7/month | N/A | N/A |
| More memory | $12/month | $20/month | $57+/month |
| Redundancy | $25/month | $150/month | $100+/month |

---

## Next Steps

1. ✅ Create Dockerfile in backend
2. ✅ Add render.yaml to root
3. ✅ Push to GitHub
4. ✅ Deploy to Render
5. ✅ Update frontend API URL
6. ✅ Deploy to Vercel
7. ✅ Set up uptime monitor
8. ✅ Test end-to-end

**Estimated time:** 20-30 minutes

**Questions?** Check the backend logs in Render dashboard or frontend console (F12) in browser for specific errors.
