# 🔧 Troubleshooting - App Not Deployed to Render

If you don't see your app deployed to Render, follow this diagnostic checklist.

---

## ❓ Quick Diagnosis - Answer These Questions

### 1. Did you actually trigger deployment?

**Did you do ONE of these?**

- [ ] **Option A**: Clicked "Create Blueprint" and "Deploy" in Render Dashboard?
- [ ] **Option B**: Pushed code to GitHub (which should trigger GitHub Actions)?
- [ ] **Option C**: Manually triggered deployment in Render?

**If None of Above**: → Go to **Step 1: Trigger Deployment** below

---

### 2. Check Render Dashboard

**Go to**: https://dashboard.render.com

**Do you see these services listed?**
- [ ] `mortgage-graph-api`
- [ ] `mortgage-graph-ui`
- [ ] `mortgage-graph-migrations`
- [ ] `mortgage-graph-gds-jobs`

**If you don't see services**: → Go to **Step 2: Create Services** below

**If you DO see services**: → Check their status next

---

### 3. Check Service Status

**For each service in Render Dashboard:**

```
Service Status:
- ❓ Green checkmark = Running ✅
- ❓ Yellow spinning = Building ⏳
- ❓ Red X = Failed ❌
- ❓ Gray = Not started
```

**What colors do you see?**

- [ ] All Green ✅ → Jump to **Step 4: Access Services** 
- [ ] Some Yellow ⏳ → Jump to **Step 3: Wait for Build**
- [ ] Some Red ❌ → Jump to **Step 5: Check Logs**

---

## 🔧 Troubleshooting Steps

### Step 1: Trigger Deployment

#### Method A: Use Render Blueprint (EASIEST)

1. **Go to**: https://dashboard.render.com
2. **Click**: "New" → "Blueprint"
3. **Paste repo**: `https://github.com/prakashpujari/GenAI-Usecases`
4. **Click**: "Connect" (authorize GitHub if needed)
5. **Click**: "Create Blueprint"
6. **Review** the 4 services shown
7. **Click**: "Deploy" (big button at bottom)

**Expected**: Services start building (yellow status)

#### Method B: Use GitHub Actions

1. **Push code to main**:
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Check GitHub Actions**: https://github.com/prakashpujari/GenAI-Usecases/actions
   - Should see "Deploy to Render" workflow running
   - Wait for it to complete

**Expected**: Workflow triggers and calls Render API

---

### Step 2: Create Services

If services don't exist in Render:

**You MUST use the Render Blueprint method** (Method A in Step 1)

1. Go to https://dashboard.render.com
2. Click "New" → "Blueprint"
3. Paste: `https://github.com/prakashpujari/GenAI-Usecases`
4. Click "Connect" and authorize
5. Render auto-detects `render.yaml`
6. Shows all 4 services from `render.yaml`
7. Click "Create Blueprint"
8. Click "Deploy"

---

### Step 3: Wait for Build

Services are **building** (yellow status = normal).

**What to do**: Wait 10-15 minutes

**Why**: Services need time to:
- Pull code from GitHub
- Build Docker images
- Install dependencies
- Start services
- Run health checks

**Monitor progress**:
1. Render Dashboard → Service name
2. **Deployments** tab → See build progress
3. **Logs** tab → See what's happening

**Check every 2-3 minutes**, don't refresh too often.

---

### Step 4: Access Services

**Once status is Green** ✅:

1. **Get service URLs**:
   - Render Dashboard → Service name
   - Copy the URL from top of page

2. **Expected URLs**:
   ```
   https://mortgage-graph-ui.onrender.com
   https://mortgage-graph-api.onrender.com
   ```

3. **Test them**:
   ```bash
   # Test API
   curl https://mortgage-graph-api.onrender.com/health

   # Open frontend in browser
   https://mortgage-graph-ui.onrender.com
   ```

---

### Step 5: Check Logs for Errors

**If service status is Red** ❌:

1. **Go to**: Render Dashboard → Service name
2. **Click**: **Logs** tab
3. **Look for**: Error messages (red text)

**Common errors and fixes**:

#### Error: "Cannot connect to Neo4j"
```
Fix: Check render.yaml has correct Aura credentials
- NEO4J_URI should be: neo4j+s://5e8389cd.databases.neo4j.io
- NEO4J_USERNAME should be: 5e8389cd
- NEO4J_PASSWORD should be: X5jQWpBNYLpnRtZEI13ntnWnpKCz1vkOOecIyWiGVwc
```

#### Error: "Port already in use"
```
Fix: Render auto-assigns ports. This shouldn't happen.
- Restart service: Service → Redeploy
```

#### Error: "npm ERR!" or "pip ERR!"
```
Fix: Dependency installation failed
- Check package.json (frontend) has correct packages
- Check requirements.txt (backend) has correct packages
- Common: Missing comma in JSON, syntax errors
```

#### Error: "Module not found"
```
Fix: Missing Python module or JS package
- Check all imports in code
- Reinstall dependencies locally to verify
```

#### Error: "Build command failed"
```
Fix: Check build command in render.yaml
- Frontend build should create dist/ folder
- Backend doesn't need build step
```

**Can't find the error?**
- Scroll up in logs
- Look for first "ERROR" message
- Copy the full error message

---

## 🔍 Verify Configuration

### Check render.yaml

**File should exist**: `Graph-db/render.yaml`

```bash
# Check it exists
ls -la Graph-db/render.yaml

# Check Neo4j credentials are in file
grep -A2 "NEO4J_URI" Graph-db/render.yaml
```

**Should see**:
```yaml
- key: NEO4J_URI
  value: neo4j+s://5e8389cd.databases.neo4j.io
```

### Check GitHub Connection

1. Go to https://dashboard.render.com
2. Click on service
3. **Settings** tab
4. Look for **Repository**: should say `prakashpujari/GenAI-Usecases`

If it says something else or shows error → Reconnect GitHub

---

## ⚡ Quick Fixes

### "I deployed but nothing happened"

```bash
# Push code to trigger GitHub Actions
git add .
git commit -m "Trigger deployment"
git push origin main

# Check GitHub Actions
https://github.com/prakashpujari/GenAI-Usecases/actions
```

### "Services won't start"

1. Check logs for specific error (Step 5)
2. Verify Neo4j Aura instance is running
3. Verify credentials in render.yaml are correct
4. Try clicking "Redeploy" in Render dashboard

### "Frontend loads but can't reach API"

1. Check API service is running (green status)
2. Test API directly: `https://mortgage-graph-api.onrender.com/health`
3. Check browser console for CORS errors (F12 → Console)
4. Clear browser cache (Ctrl+Shift+Delete)

### "Frontend URL shows 404"

1. Render Dashboard → UI service → **Logs** tab
2. Look for build errors
3. Check `npm run build` works locally:
   ```bash
   cd Graph-db/frontend
   npm install
   npm run build
   ```

---

## 📞 Get Help

### Check These Files

- `DEPLOY_NOW.md` — Detailed deployment steps
- `RENDER_DEPLOYMENT.md` — Comprehensive troubleshooting
- `render.yaml` — Configuration file

### External Help

- **Render Support**: https://render.com/docs
- **Neo4j Support**: https://neo4j.com/docs/aura/
- **GitHub Actions Help**: https://docs.github.com/en/actions

### Run This Diagnostic

```bash
echo "=== Git Status ==="
git status

echo "=== Recent Commits ==="
git log --oneline -5

echo "=== render.yaml exists ==="
ls -la Graph-db/render.yaml

echo "=== GitHub Actions Workflow ==="
ls -la ../.github/workflows/

echo "=== Done ==="
```

---

## 📋 Quick Checklist

Before contacting support, verify:

- [ ] GitHub repo is public or Render has access
- [ ] `render.yaml` exists and has correct syntax
- [ ] Neo4j Aura instance exists and is running
- [ ] Neo4j credentials are correct in `render.yaml`
- [ ] Render services are created (visible in dashboard)
- [ ] Checked logs for error messages
- [ ] Services have been building for at least 10 minutes
- [ ] Tried "Redeploy" if services failed

---

## 🎯 Expected Timeline

| Time | What Happens |
|------|--------------|
| 0-2 min | Services created, start building (yellow) |
| 2-10 min | Installing dependencies, building images |
| 10-15 min | Services start, health checks run |
| 15+ min | Services should be green ✅ and running |

**If still yellow after 20 min**: Check logs for errors

**If red**: Definitely check logs

---

## Help Me Diagnose

**If nothing works, answer these**:

1. Do you see any services in Render Dashboard?
2. What are their colors (green/yellow/red)?
3. Any error messages visible in Logs tab?
4. Did you see "Deploy" button? Did you click it?
5. What's the GitHub repo URL you used?
6. Did you authorize Render to access GitHub?

**Then I can help you fix it!**

---

**Status**: Configuration is ✅ Ready - just needs to be deployed!
