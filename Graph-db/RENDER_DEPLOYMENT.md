# Render Deployment Guide

## Overview

This guide walks you through deploying the Mortgage Graph Platform (React + FastAPI + Neo4j) to Render using the **`render.yaml` Blueprint** (recommended) or manual setup.

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Account**: Already set up with the repository
3. **Render API Key**: `rnd_XfRqbVaGn5DMF0FRZhqhRX1hU33u`
4. **Neo4j Instance**: Use Neo4j Cloud Aura (free tier) or your own instance

---

## QUICK START: Blueprint Deployment (Recommended)

### 1. Set Up Neo4j First

**Go to Neo4j Cloud Aura:**
1. Visit https://aura.neo4j.io
2. Create a free Neo4j instance
3. Copy the connection details:
   - **URI**: `neo4j+s://xxxx.databases.neo4j.io` or `bolt://xxxx:7687`
   - **Username**: `neo4j`
   - **Password**: (your secure password)

### 2. Deploy with Blueprint

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Blueprint**
3. Paste GitHub repo: `https://github.com/prakashpujari/GenAI-Usecases`
4. Render auto-detects `render.yaml` and shows:
   - ✅ `mortgage-graph-api` (FastAPI)
   - ✅ `mortgage-graph-ui` (React)
   - ✅ `mortgage-graph-migrations` (Cron)
   - ✅ `mortgage-graph-gds-jobs` (Cron)
5. Click **Create Blueprint**

### 3. Configure Environment Variables

When Render prompts, set these for each service:

**Backend Service (`mortgage-graph-api`)**:
```env
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j
STORAGE_BACKEND=neo4j
LOG_LEVEL=info
WORKERS=4
```

**Frontend Service (`mortgage-graph-ui`)**:
```env
VITE_API_BASE_URL=https://mortgage-graph-api.onrender.com
VITE_API_TIMEOUT=30000
NODE_ENV=production
```

### 4. Deploy

Click **Deploy Blueprint** and wait for all services to be healthy (~5-10 minutes)

### 5. Access Your Deployment

- **Frontend**: https://mortgage-graph-ui.onrender.com
- **Backend API**: https://mortgage-graph-api.onrender.com
- **API Docs**: https://mortgage-graph-api.onrender.com/docs

---

## DETAILED SETUP: Manual Blueprint Configuration

### Render.yaml Structure

The `render.yaml` file defines all services in one configuration. Key sections:

```yaml
services:
  - type: web              # FastAPI backend
  - type: web              # React frontend
  - type: cron             # Daily migrations
  - type: cron             # Daily GDS jobs
```

### Environment Variables in render.yaml

All services reference environment variables. You set their **values** in Render Dashboard:

| Service | Variable | Example Value |
|---------|----------|----------------|
| API | `NEO4J_URI` | `neo4j+s://abc123.databases.neo4j.io:7687` |
| API | `NEO4J_USER` | `neo4j` |
| API | `NEO4J_PASSWORD` | (your secure password) |
| UI | `VITE_API_BASE_URL` | `https://mortgage-graph-api.onrender.com` |

---

## STEP-BY-STEP MANUAL SETUP (Alternative)

### Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Account**: Already set up with the repository
3. **Neo4j Instance**: Can use Aura (free tier) or your own instance

## Step-by-Step Deployment

### 1. Prepare Neo4j Database

**Option A: Use Neo4j Aura (Recommended for Render)**
- Go to [aura.neo4j.io](https://aura.neo4j.io)
- Create a free instance
- Copy connection details (URI, username, password)

**Option B: Use existing Neo4j**
- Get your Neo4j connection string
- Ensure it's accessible from Render (public instance)

### 2. Create Environment Configuration

Store these as Render environment variables:
```env
# Neo4j
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# Application
PROJECT_NAME=Mortgage Graph Platform
ENV=production
LOG_LEVEL=INFO
TIMEZONE=UTC
STORAGE_BACKEND=neo4j
DATA_PATH=/app/data
EXPORT_PATH=/app/exports
```

### 3. Deploy FastAPI Backend

**Step 1: Create Web Service**
1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository (prakashpujari/GenAI-Usecases)
3. Configure:
   - **Name**: `mortgage-graph-api`
   - **Environment**: `Docker`
   - **Region**: Choose closest to you (e.g., us-east-1)
   - **Branch**: `main`

**Step 2: Docker Configuration**
- Render automatically detects Dockerfile
- Set Build Command: (leave empty if using root Dockerfile)
- Set Start Command:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 10000
  ```

**Step 3: Environment Variables**
1. Add all environment variables from Step 2
2. Set `PORT=10000` (Render uses this)

**Step 4: Deploy**
- Click "Deploy"
- Monitor logs (usually takes 5-10 minutes)
- Once running, note the service URL: `https://mortgage-graph-api.render.com`

### 4. Deploy React Frontend

**Step 1: Create Static Site**
1. Go to Render Dashboard → New → Static Site
2. Connect same GitHub repository
3. Configure:
   - **Name**: `mortgage-graph-ui`
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory**: `frontend/dist`

**Step 2: Deploy**
- Click "Deploy"
- Frontend builds and deploys (usually 3-5 minutes)
- Note the URL: `https://mortgage-graph-ui.onrender.com`

### 5. Configure CORS for Frontend-Backend Communication

**Update Backend Service**

Add environment variable to API service:
```env
FRONTEND_URL=https://mortgage-graph-ui.onrender.com
```

Update `app/main.py` CORS configuration:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mortgage-graph-ui.onrender.com",
        "http://localhost:5173",  # For local dev
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push this change to GitHub - Render will auto-redeploy.

### 6. Update Frontend API Base URL

The frontend's `vite.config.ts` has API proxy for local dev. For production:

**Option A: Update `.env` before build**
```env
VITE_API_BASE_URL=https://mortgage-graph-api.render.com
```

**Option B: Use Render build command to set it**
```bash
cd frontend && VITE_API_BASE_URL=https://mortgage-graph-api.render.com npm run build
```

Or update static site build command in Render dashboard:
```bash
cd frontend && VITE_API_BASE_URL=$(echo ${API_BASE_URL:-https://mortgage-graph-api.render.com}) npm install && npm run build
```

### 7. Test Deployment

**Check API Health**
```bash
curl https://mortgage-graph-api.render.com/health
# Expected response: {"status": "ok"}
```

**Access Frontend**
- Open browser: `https://mortgage-graph-ui.onrender.com`
- Should see the Mortgage Graph Platform UI
- Try navigating to Dashboard → should show API health

**Test Loan Ingestion**
```bash
curl -X POST https://mortgage-graph-api.render.com/loans/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "borrower": {"borrowerId": "B001", "name": "Test User"},
    "loan": {"loanId": "L001", "amount": 450000, "status": "submitted", "purpose": "purchase"},
    "property": {"propertyId": "P001", "address": "123 Main", "city": "Austin", "state": "TX", "zip": "73301", "type": "single_family"},
    "income": {"incomeId": "I001", "type": "w2", "employerName": "Test Co", "annualIncome": 180000},
    "documents": []
  }'
```

## Troubleshooting

### Build Failures

**Frontend build fails**
- Check `npm install` succeeds locally
- Verify `frontend/dist` is in `.gitignore` (git shouldn't include it)
- Check Node.js version (should be 18+ for Vite 5)

**Backend fails to start**
- Check all environment variables are set
- Neo4j connection string might need neo4j+s:// (not bolt://)
- Check logs in Render dashboard

### Runtime Issues

**"Cannot connect to database"**
- Verify NEO4J_URI is neo4j+s:// (secure)
- Check Neo4j credentials
- Test connection locally first

**CORS errors in frontend**
- Update CORS origins in `app/main.py`
- Redeploy API service
- Clear browser cache (Ctrl+Shift+Delete)

**Slow performance**
- Check database is free tier or has resources
- Vite build might be slow on free tier (upgrade if needed)
- API service might need more memory

### Logs

View logs in Render Dashboard:
1. Go to service page
2. Click "Logs" tab
3. Filter by time or search for errors

---

## Services Overview (from render.yaml)

### 1. FastAPI Backend (`mortgage-graph-api`)

**Type**: Web Service  
**Runtime**: Python  
**Port**: Auto-assigned by Render  
**Health Check**: `/health` endpoint

**What it does:**
- Runs FastAPI server with Uvicorn
- Connects to Neo4j database
- Exposes REST API endpoints
- Handles loan ingestion, risk analysis, graph queries

**Build Steps:**
1. Install Python dependencies: `pip install -r requirements.txt`
2. Start with: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Expected URL**: `https://mortgage-graph-api.onrender.com`

---

### 2. React Frontend (`mortgage-graph-ui`)

**Type**: Web Service (Node.js)  
**Runtime**: Node.js  
**Port**: 3000  
**Health Check**: `/` (index.html)

**What it does:**
- Builds React + Vite SPA
- Serves compiled frontend
- Proxies `/api/*` to backend
- Shows Dashboard, Loans, Risk, Graph, Jobs pages

**Build Steps:**
1. Install npm dependencies: `npm ci`
2. Build: `npm run build` (creates `frontend/dist`)
3. Preview/Serve: `npm run preview`

**Expected URL**: `https://mortgage-graph-ui.onrender.com`

---

### 3. Schema Migration Job (`mortgage-graph-migrations`)

**Type**: Cron Job (background task)  
**Runtime**: Python  
**Schedule**: Daily at 2 AM UTC  
**Command**: `python -m app.etl.migrate_schema`

**What it does:**
- Initializes Neo4j schema (nodes, relationships, indexes)
- Idempotent (safe to run multiple times)
- Runs automatically each day
- Can be triggered manually from Render dashboard

---

### 4. GDS Analytics Job (`mortgage-graph-gds-jobs`)

**Type**: Cron Job (background task)  
**Runtime**: Python  
**Schedule**: Daily at 3 AM UTC (after migrations)  
**Command**: `python -m app.gds.run_gds_jobs`

**What it does:**
- Runs Graph Data Science algorithms
- Computes centrality, community detection, etc.
- Updates graph metrics
- Runs automatically each day

---

## Verifying Deployment

### Backend Health Check

```bash
# Check API is running
curl https://mortgage-graph-api.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Frontend Access

1. Open https://mortgage-graph-ui.onrender.com
2. Navigate to **Dashboard** tab
3. Should show API health status

### Test Loan Ingestion

```bash
curl -X POST https://mortgage-graph-api.onrender.com/loans/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "borrower": {"borrowerId": "B001", "name": "Test User"},
    "loan": {"loanId": "L001", "amount": 450000, "status": "submitted", "purpose": "purchase"},
    "property": {"propertyId": "P001", "address": "123 Main", "city": "Austin", "state": "TX", "zip": "73301", "type": "single_family"},
    "income": {"incomeId": "I001", "type": "w2", "employerName": "Test Co", "annualIncome": 180000},
    "documents": []
  }'
```

---

## Monitoring & Troubleshooting

### View Service Logs

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on service name
3. **Logs** tab shows real-time output
4. Search for errors or filter by time

### Common Issues

**Backend won't start:**
- Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD are set
- Verify Neo4j instance is running and accessible
- Check logs for connection errors

**Frontend won't build:**
- Ensure `frontend/package.json` and dependencies are correct
- Check Node.js version compatibility
- Frontend needs Node 18+

**Frontend can't reach API:**
- Verify `VITE_API_BASE_URL` matches backend URL
- Check CORS is enabled (should be default)
- Clear browser cache (Ctrl+Shift+Delete)

**Cron jobs not running:**
- Check **Cron** tab in Render dashboard
- Can manually trigger from dashboard
- Check logs for execution status

---

## Advanced: Custom Domain

### Add Custom Domain to Frontend

1. Go to `mortgage-graph-ui` service
2. **Settings** → **Custom Domain**
3. Add your domain (e.g., `mortgage.example.com`)
4. Follow DNS setup instructions

### Add Custom Domain to API

1. Go to `mortgage-graph-api` service
2. **Settings** → **Custom Domain**
3. Add your domain (e.g., `api.mortgage.example.com`)
4. Update frontend `VITE_API_BASE_URL` if needed

---

## Production Best Practices

### 1. Security
- ✅ Use neo4j+s:// for encrypted connection
- ✅ Set strong Neo4j password
- ✅ Don't commit `.env` files with secrets
- ✅ Use Render's environment variable feature
- [ ] Add authentication to API (future)

### 2. Monitoring
- Set up error tracking (Sentry)
- Monitor Neo4j query performance
- Set up uptime monitoring

### 3. Database Backups
- Enable Neo4j Aura backups
- Test restore procedure monthly

### 4. Scaling
- Free tier limits: 0.5 CPU, 512 MB RAM
- If hitting limits, upgrade to paid tier
- Consider dedicated Neo4j instance

## Cost Estimation

| Service | Free Tier | Cost |
|---------|-----------|------|
| Render Web Service | $0 (15 min cold start) | $7-12/month |
| Render Static Site | $0 | Free |
| Neo4j Aura Free | Free | Free (limited) |
| **Total** | | **$0-12/month** |

## Continuous Deployment

Render automatically redeploys when you push to `main` branch:

1. Make changes locally
2. Commit and push: `git push origin main`
3. Render automatically:
   - Pulls latest code
   - Rebuilds Docker image (API)
   - Rebuilds frontend
   - Deploys new version

## Environment-Specific URLs

| Environment | Frontend | API |
|-------------|----------|-----|
| Local Dev | http://localhost:5173 | http://localhost:8000 |
| Render Prod | mortgage-graph-ui.onrender.com | mortgage-graph-api.render.com |

## Rollback

If something breaks:

1. **Go to service page** in Render
2. **Click "Deployments"** tab
3. **Select previous** working deployment
4. **Click "Redeploy"**

## Next Steps

After deployment:

1. ✅ Monitor for errors in Render logs
2. ✅ Test all pages (Dashboard, Loans, Risk, Graph, Jobs)
3. ✅ Load test with some sample loans
4. ✅ Set up uptime monitoring
5. ✅ Configure auto-scaling if needed

## Support

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Neo4j Docs**: https://neo4j.com/docs

---

**Deployment Status**: ✅ Ready for production
**Last Updated**: 2026-06-06
