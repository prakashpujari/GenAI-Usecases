# Setup GitHub Secrets for Automatic Deployment

## Your Service IDs (SAVE THESE!)

```
API Service ID:  srv-d8hgie3eo5us7386bs2g
UI Service ID:   srv-d8hidqi8pkls73cfgr8g
Render API Key:  rnd_XfRqbVaGn5DMF0FRZhqhRX1hU33u
```

---

## ✅ Add GitHub Secrets (3 minutes)

### Step 1: Go to GitHub Settings
1. Open: https://github.com/prakashpujari/GenAI-Usecases
2. Click **Settings** (top right)
3. Go to **Secrets and variables** → **Actions**

### Step 2: Add Secret #1 - RENDER_API_KEY

1. Click **"New repository secret"**
2. **Name**: `RENDER_API_KEY`
3. **Value**: 
   ```
   rnd_XfRqbVaGn5DMF0FRZhqhRX1hU33u
   ```
4. Click **"Add secret"**

### Step 3: Add Secret #2 - RENDER_SERVICE_ID_API

1. Click **"New repository secret"**
2. **Name**: `RENDER_SERVICE_ID_API`
3. **Value**:
   ```
   srv-d8hgie3eo5us7386bs2g
   ```
4. Click **"Add secret"**

### Step 4: Add Secret #3 - RENDER_SERVICE_ID_UI

1. Click **"New repository secret"**
2. **Name**: `RENDER_SERVICE_ID_UI`
3. **Value**:
   ```
   srv-d8hidqi8pkls73cfgr8g
   ```
4. Click **"Add secret"**

---

## ✅ Verify Secrets Added

You should see 3 secrets listed:
- ✅ RENDER_API_KEY
- ✅ RENDER_SERVICE_ID_API
- ✅ RENDER_SERVICE_ID_UI

---

## 🚀 Deploy (After Secrets Are Added)

**Once secrets are configured**, I'll push code to GitHub which will automatically:

1. Trigger GitHub Actions workflow
2. Call Render API with your service IDs
3. Deploy to your services
4. Services will rebuild and go live

---

## Status

- ✅ render.yaml configured
- ✅ Service IDs saved
- ⏳ Waiting for GitHub secrets to be added
- ⏳ Then automatic deployment!

---

**Next**: Add the 3 secrets above, then reply "Secrets added!"
