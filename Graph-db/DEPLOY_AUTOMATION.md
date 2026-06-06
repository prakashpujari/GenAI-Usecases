# Automatic Deployment Setup

This guide sets up automated deployment to Render using GitHub Actions and git hooks.

---

## Option 1: GitHub Actions (Recommended) ✅

Automatically deploy to Render on every push to `main`.

### Setup (5 minutes)

#### Step 1: Get Render Service IDs

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on `mortgage-graph-api` service
3. Copy the service ID from URL: `https://dashboard.render.com/services/{SERVICE_ID}`
4. Repeat for `mortgage-graph-ui` service

#### Step 2: Create GitHub Secrets

1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

| Name | Value |
|------|-------|
| `RENDER_API_KEY` | `rnd_XfRqbVaGn5DMF0FRZhqhRX1hU33u` |
| `RENDER_SERVICE_ID_API` | (paste API service ID) |
| `RENDER_SERVICE_ID_UI` | (paste UI service ID) |

#### Step 3: Verify Workflow

1. Go to GitHub repo → **Actions** tab
2. You should see "Deploy to Render" workflow
3. Workflow is ready to trigger on push

### How It Works

**Trigger**: Push to `main` branch  
**Actions**:
1. Validates code
2. Calls Render API to trigger deployment
3. Shows deployment status

**Result**: Services auto-update without manual intervention

### Manual Trigger (Optional)

```bash
git add .
git commit -m "Your changes"
git push origin main
```

→ GitHub Actions automatically deploys to Render

---

## Option 2: Local Git Hooks

Run validation before pushing (prevents bad deployments).

### Setup (2 minutes)

#### Step 1: Copy Hook File

From `Graph-db/.git-hooks/pre-push.sh` to `.git/hooks/pre-push`:

```powershell
# Windows PowerShell
Copy-Item -Path "Graph-db\.git-hooks\pre-push.sh" -Destination ".git\hooks\pre-push" -Force
```

Or on Mac/Linux:
```bash
cp Graph-db/.git-hooks/pre-push.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

#### Step 2: Make Executable

```powershell
# Windows - ensure Git can execute it
icacls ".git\hooks\pre-push" /grant:r "$env:username`:F"
```

### What It Checks

Before pushing to `main`, validates:
- ✓ No uncommitted changes
- ✓ `render.yaml` syntax is valid
- ✓ `requirements.txt` exists
- ✓ `frontend/package.json` exists
- ✓ Tests pass (if test suite exists)

### Example Usage

```bash
git add .
git commit -m "Update API"
git push origin main
```

**Output**:
```
🔍 Running pre-push validation...
📤 Pushing to main branch - running validation checks...
✓ Validating render.yaml...
🧪 Running tests...
✅ All checks passed!
🚀 Ready to deploy to Render on push
```

---

## Option 3: Render's Native Auto-Deploy (Default)

Render automatically deploys on every push (no setup needed!).

### How It Works

1. Repository connected to Render
2. Any push to `main` triggers auto-deploy
3. New services deployed in ~5-10 minutes
4. No additional configuration needed

### Monitor Auto-Deploys

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click service → **Deployments** tab
3. See auto-deploy status and logs

---

## Deployment Flow

```
Developer makes changes
    ↓
git push origin main
    ↓
GitHub Actions triggers (Option 1)
    ↓
Render API receives deployment request
    ↓
Services rebuild and deploy
    ↓
Status available in Render Dashboard
```

---

## Monitoring Deployments

### Via GitHub Actions

1. Go to repo → **Actions** tab
2. Click "Deploy to Render" workflow
3. See deployment status and logs

### Via Render Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click service name
3. **Deployments** tab shows all deployments
4. **Logs** tab shows build/runtime logs

---

## What Gets Deployed

**On every push to `main`:**
- ✅ FastAPI backend (Graph-db/)
- ✅ React frontend (Graph-db/frontend/)
- ✅ Cron jobs (migrations, GDS)

**Skipped if no changes:**
- Paths monitored: `Graph-db/**`, `render.yaml`
- Changes to other paths don't trigger deploy

---

## Rollback

If something goes wrong:

1. Go to Render Dashboard → Service → **Deployments**
2. Find previous working deployment
3. Click **Redeploy**

**No code changes needed** - Render handles it.

---

## Disable Auto-Deploy (Optional)

If you want manual control:

1. Service → **Settings**
2. Toggle **Auto-Deploy** OFF
3. Deploy manually when needed

---

## Cost Impact

- ✅ GitHub Actions: Free (2,000 minutes/month included)
- ✅ Render deployments: No additional cost
- ✅ Auto-deploy doesn't increase charges

---

## Troubleshooting

### "Deployment failed in GitHub Actions"

Check:
1. GitHub Actions → workflow logs
2. Verify secrets are set correctly
3. Render service IDs are correct

```bash
# Test Render API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.render.com/v1/services
```

### "Render says service not found"

- Verify service IDs are correct
- Check service exists in Render Dashboard
- IDs are case-sensitive

### "Pre-push hook is too strict"

Edit `.git/hooks/pre-push` to remove checks you don't want.

---

## Advanced: Custom Deployment Steps

Edit `.github/workflows/deploy-to-render.yml` to add:

```yaml
- name: Run backend tests
  run: |
    pip install -r requirements.txt
    pytest -q

- name: Build frontend
  run: |
    cd frontend
    npm install
    npm run build
```

---

## Summary

| Method | Setup | Auto-Deploy | Validation |
|--------|-------|-------------|-----------|
| Render Native | ✅ 0 min | ✅ Yes | ❌ No |
| GitHub Actions | ✅ 5 min | ✅ Yes | ✅ Optional |
| Git Hooks | ✅ 2 min | ❌ Manual | ✅ Yes |

**Recommended**: Use Render's native auto-deploy (already working!) + optional GitHub Actions for monitoring.

---

## Quick Reference

```bash
# Deploy to Render (automatic)
git add .
git commit -m "Your changes"
git push origin main

# Watch deployment
# → GitHub Actions: https://github.com/prakashpujari/GenAI-Usecases/actions
# → Render: https://dashboard.render.com

# Check status
# Frontend: https://mortgage-graph-ui.onrender.com
# API: https://mortgage-graph-api.onrender.com/health
```

---

**Status**: ✅ Auto-deployment ready!

Push to `main` and watch your changes go live automatically.
