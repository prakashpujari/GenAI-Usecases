# Render Deployment - Quick Setup Guide

## Your Neo4j Aura Details ✅

```
Instance Name:  mortgage_neo4j_Instance
Instance ID:    5e8389cd

Connection URI:    neo4j+s://5e8389cd.databases.neo4j.io
Username:          5e8389cd
Password:          X5jQWpBNYLpnRtZEI13ntnWnpKCz1vkOOecIyWiGVwc
Database:          5e8389cd
```

✅ **Already configured in `render.yaml`** — no additional setup needed for Neo4j!

---

## Deploy to Render in 3 Steps

### Step 1: Go to Render Dashboard

1. Open https://dashboard.render.com
2. Click **New** → **Blueprint**

### Step 2: Connect Your Repository

1. Paste repository: `https://github.com/prakashpujari/GenAI-Usecases`
2. Click **Connect GitHub**
3. Authorize Render (if prompted)

### Step 3: Deploy

1. Render auto-detects `render.yaml`
2. Shows 4 services:
   - ✅ `mortgage-graph-api` (FastAPI)
   - ✅ `mortgage-graph-ui` (React)
   - ✅ `mortgage-graph-migrations` (Cron)
   - ✅ `mortgage-graph-gds-jobs` (Cron)
3. Click **Create Blueprint**
4. Review and click **Deploy**

**Done!** ✅

---

## Expected URLs (After ~10 minutes)

| Service | URL |
|---------|-----|
| Frontend | https://mortgage-graph-ui.onrender.com |
| Backend API | https://mortgage-graph-api.onrender.com |
| API Docs | https://mortgage-graph-api.onrender.com/docs |

---

## Verify Deployment

### Check Backend Health

```bash
curl https://mortgage-graph-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Access Frontend

Open https://mortgage-graph-ui.onrender.com in your browser

---

## Configuration Details

### Backend Service (`mortgage-graph-api`)

**Build**: `pip install -r requirements.txt`  
**Start**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables** (auto-set from render.yaml):
- `NEO4J_URI` = neo4j+s://5e8389cd.databases.neo4j.io
- `NEO4J_USERNAME` = 5e8389cd
- `NEO4J_PASSWORD` = X5jQWpBNYLpnRtZEI13ntnWnpKCz1vkOOecIyWiGVwc
- `NEO4J_DATABASE` = 5e8389cd
- `STORAGE_BACKEND` = neo4j
- `LOG_LEVEL` = info
- `WORKERS` = 4

### Frontend Service (`mortgage-graph-ui`)

**Build**: `npm ci && npm run build` (in `frontend/` directory)  
**Start**: `npm run preview`

**Environment Variables** (auto-set from render.yaml):
- `VITE_API_BASE_URL` = https://mortgage-graph-api.onrender.com
- `VITE_API_TIMEOUT` = 30000
- `NODE_ENV` = production

### Cron Jobs

**Schema Migration** (`mortgage-graph-migrations`)
- Schedule: Daily at 2 AM UTC
- Command: `python -m app.etl.migrate_schema`

**GDS Analytics** (`mortgage-graph-gds-jobs`)
- Schedule: Daily at 3 AM UTC
- Command: `python -m app.gds.run_gds_jobs`

---

## Troubleshooting

### "Failed to connect to Neo4j"

Check:
1. Neo4j Aura instance is running (https://aura.neo4j.io)
2. Your IP is allowed (check firewall)
3. Neo4j credentials are correct (already in `render.yaml`)

### "Frontend can't reach API"

Check:
1. Backend service is running (check status in Render dashboard)
2. Visit `https://mortgage-graph-api.onrender.com/docs` to confirm API is up
3. Browser console for CORS errors (press F12 → Console)

### "Build failed"

Check Render logs:
1. Go to service page
2. Click **Logs** tab
3. Look for error messages
4. Common issues:
   - Node.js version mismatch (need Node 18+)
   - Missing dependencies
   - Invalid Dockerfile

---

## Continuous Deployment

Every push to `main` branch auto-deploys:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render automatically:
1. Pulls latest code
2. Rebuilds services
3. Deploys new version

---

## Monitoring

### View Logs

1. Render dashboard → Service name
2. **Logs** tab shows real-time output
3. Filter by service or search for errors

### Check Service Health

Render dashboard shows:
- ✅ Green = Running
- ⚠️ Yellow = Building
- ❌ Red = Failed

---

## Next Steps

1. ✅ Deploy to Render (follow 3 steps above)
2. ✅ Test health endpoint: `curl https://mortgage-graph-api.onrender.com/health`
3. ✅ Open frontend: https://mortgage-graph-ui.onrender.com
4. ✅ Try loan ingestion in the UI
5. ✅ Check GDS jobs status in Jobs Monitor page

---

## Support

- **Render docs**: https://render.com/docs
- **Neo4j Aura docs**: https://neo4j.com/docs/aura/
- **FastAPI docs**: https://fastapi.tiangolo.com
- **Project README**: See `RENDER_DEPLOYMENT.md`

---

**Ready to deploy!** 🚀

Your Aura credentials are already embedded in `render.yaml`. Just hit deploy!
