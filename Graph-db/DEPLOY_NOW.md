# Deploy Complete App to Render NOW

Follow these steps to deploy the entire application to Render immediately and set up automatic deployment for future changes.

---

## ✅ Pre-Deployment Checklist

Before deploying, verify everything is ready:

- [x] `render.yaml` configured with Neo4j Aura credentials
- [x] GitHub Actions workflow created (`.github/workflows/deploy-to-render.yml`)
- [x] Frontend build configuration ready
- [x] Backend configuration ready
- [x] Cron jobs configured

**Status**: ✅ Ready to deploy!

---

## 🚀 Deploy Now (3 Options)

### Option 1: Render Blueprint (RECOMMENDED - Easiest)

**Best for**: First-time complete deployment

#### Step 1: Go to Render Dashboard
https://dashboard.render.com

#### Step 2: Click "New" → "Blueprint"

#### Step 3: Paste Repository URL
```
https://github.com/prakashpujari/GenAI-Usecases
```

#### Step 4: Authorize GitHub
Click "Connect" and authorize Render

#### Step 5: Review Services
Render detects `render.yaml` and shows:
- ✅ `mortgage-graph-api` (FastAPI backend)
- ✅ `mortgage-graph-ui` (React frontend)
- ✅ `mortgage-graph-migrations` (Cron job)
- ✅ `mortgage-graph-gds-jobs` (Cron job)

#### Step 6: Create Blueprint
Click **"Create Blueprint"**

#### Step 7: Deploy All Services
Click **"Deploy"**

⏱️ **Wait Time**: 10-15 minutes for all services to start

---

### Option 2: Git Push (After Initial Setup)

**Best for**: Automatic deployment on code changes

#### Prerequisites
1. GitHub Actions secrets configured (see below)
2. Render services already created

#### Deploy Process
```bash
# Make your changes
git add .
git commit -m "Your changes"

# Push to main - automatic deployment!
git push origin main
```

**What happens automatically**:
1. GitHub Actions workflow triggers
2. Calls Render API to deploy
3. Services rebuild and update
4. Changes live in ~5-10 minutes

---

### Option 3: Manual Trigger via Render Dashboard

**Best for**: Deploying without code changes

#### In Render Dashboard
1. Go to service (e.g., `mortgage-graph-api`)
2. Click **"Manual Deploy"** or **"Redeploy"** button
3. Select a deployment to redeploy

---

## 🔐 Configure GitHub Actions (For Auto-Deploy)

### Step 1: Get Service IDs from Render

1. Go to https://dashboard.render.com
2. Click on **`mortgage-graph-api`** service
3. Look at browser URL: `https://dashboard.render.com/services/{SERVICE_ID}`
   - Copy the `{SERVICE_ID}` part
4. Repeat for **`mortgage-graph-ui`** service

### Step 2: Add GitHub Secrets

1. Go to GitHub repo: https://github.com/prakashpujari/GenAI-Usecases
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add these THREE secrets:

#### Secret 1: RENDER_API_KEY
```
Name:  RENDER_API_KEY
Value: rnd_XfRqbVaGn5DMF0FRZhqhRX1hU33u
```

#### Secret 2: RENDER_SERVICE_ID_API
```
Name:  RENDER_SERVICE_ID_API
Value: (paste your API service ID from step 1)
```

#### Secret 3: RENDER_SERVICE_ID_UI
```
Name:  RENDER_SERVICE_ID_UI
Value: (paste your UI service ID from step 1)
```

### Step 3: Verify GitHub Actions

1. Go to repo → **Actions** tab
2. You should see **"Deploy to Render"** workflow
3. Status shows: **"Ready to run"** or **"Waiting"**

---

## 📊 After First Deployment

### Check Deployment Status

**In Render Dashboard**:
1. Go to https://dashboard.render.com
2. Click service name
3. **Deployments** tab shows all deployments
4. Green checkmark = ✅ Success

**In GitHub Actions**:
1. Go to repo → **Actions** tab
2. Click "Deploy to Render" workflow
3. See deployment status and logs

### Access Your Live App

Once deployed, services are live at:

| Service | URL |
|---------|-----|
| **Frontend** | https://mortgage-graph-ui.onrender.com |
| **API** | https://mortgage-graph-api.onrender.com |
| **API Docs** | https://mortgage-graph-api.onrender.com/docs |
| **Health Check** | https://mortgage-graph-api.onrender.com/health |

### Verify Everything Works

```bash
# Test API health
curl https://mortgage-graph-api.onrender.com/health

# Expected response:
# {"status": "healthy", "database": "connected"}

# Test frontend
# Open https://mortgage-graph-ui.onrender.com in browser
```

---

## 🔄 Automatic Deployment (From Now On)

After initial setup, **every push to `main` automatically deploys**:

```bash
# Update your code
vim Graph-db/app/main.py

# Commit changes
git add Graph-db/app/main.py
git commit -m "Update API logic"

# Push to main
git push origin main

# ✨ GitHub Actions automatically:
# 1. Runs validation
# 2. Calls Render API
# 3. Services redeploy
# 4. Changes live in ~5-10 minutes
```

---

## 🛠️ Troubleshooting

### "Blueprint Creation Failed"
- Check GitHub authorization
- Verify repository is public or Render has access
- Try again or use Manual Deploy option

### "Services Won't Start"
**Check logs in Render Dashboard**:
1. Click service
2. **Logs** tab
3. Look for error messages

**Common issues**:
- Neo4j credentials wrong: Check `render.yaml`
- Port conflict: Render assigns automatically
- Build failed: Check Python/Node.js versions

### "GitHub Actions Not Running"
- Verify workflow file exists: `.github/workflows/deploy-to-render.yml`
- Check secrets are set correctly
- Workflow triggered on push to `main` branch

### "Frontend Can't Reach API"
1. Verify API service is running
2. Check `VITE_API_BASE_URL` in render.yaml
3. Clear browser cache (Ctrl+Shift+Delete)

---

## 📋 Deployment Checklist

Use this to verify everything is deployed:

### Backend (`mortgage-graph-api`)
- [ ] Service is running (green status in Render)
- [ ] Health check returns 200: `curl https://mortgage-graph-api.onrender.com/health`
- [ ] API docs accessible: https://mortgage-graph-api.onrender.com/docs
- [ ] Connected to Neo4j Aura

### Frontend (`mortgage-graph-ui`)
- [ ] Service is running (green status in Render)
- [ ] Loads without errors: https://mortgage-graph-ui.onrender.com
- [ ] Can navigate between pages
- [ ] Dashboard shows API health status

### Cron Jobs
- [ ] `mortgage-graph-migrations` shows in Services list
- [ ] `mortgage-graph-gds-jobs` shows in Services list
- [ ] Can manually trigger from Render dashboard

### Automatic Deployment
- [ ] GitHub Actions workflow is active
- [ ] Render secrets configured (3 secrets)
- [ ] Pushing to `main` triggers deployment

---

## 📊 Monitor Your Deployment

### Real-Time Monitoring

**GitHub Actions**:
```
https://github.com/prakashpujari/GenAI-Usecases/actions
```

**Render Dashboard**:
```
https://dashboard.render.com
```

### View Logs Anytime

**In Render**:
1. Click service
2. **Logs** tab shows last 100 lines
3. Filter by time or search for errors

**In GitHub**:
1. Go to **Actions** tab
2. Click workflow run
3. See step-by-step logs

---

## 🎯 Next Steps

### Immediate (Now)
1. ✅ Deploy using Render Blueprint (Option 1)
2. ✅ Verify services are running
3. ✅ Test health endpoints

### Within 1 Hour
1. ✅ Configure GitHub Actions secrets
2. ✅ Test automatic deployment
3. ✅ Make a test commit and push

### Going Forward
1. Code changes automatically deploy
2. Monitor Render dashboard for status
3. Check logs if issues arise
4. Scale up services as needed

---

## 💡 Tips & Tricks

### Speed Up Builds
- Frontend builds faster on paid Render plans
- Backend startup can be optimized with smaller dependencies

### Reduce Costs
- Use Render free tier for testing
- Upgrade only services that need it
- Monitor resource usage in dashboard

### Enable Auto-Scaling
- Dashboard: Service → Settings → Autoscaling
- Set min/max instances based on load

### Custom Domain
- Service → Settings → Custom Domain
- Add your domain (e.g., `api.yourcompany.com`)

---

## 📞 Support & Resources

**Render Documentation**:
https://render.com/docs

**Neo4j Aura Help**:
https://neo4j.com/docs/aura/

**GitHub Actions Help**:
https://docs.github.com/en/actions

**Project Documentation**:
- See `RENDER_DEPLOYMENT.md` for detailed setup
- See `RENDER_QUICK_SETUP.md` for quick reference
- See `DEPLOY_AUTOMATION.md` for automation options

---

## ✅ Summary

**Status**: Everything is configured and ready!

| Step | Status |
|------|--------|
| render.yaml configured | ✅ Done |
| GitHub Actions workflow | ✅ Done |
| Neo4j Aura set up | ✅ Done |
| Ready to deploy | ✅ Yes |
| Ready for auto-deploy | ✅ Yes (after secrets) |

**Time to deployment**: 15 minutes  
**Time to auto-deploy setup**: 5 minutes  
**Time to next automatic update**: 10 minutes after push  

---

**🚀 Ready to deploy? Start with Option 1 above!**

Your complete app will be live in 15 minutes.
