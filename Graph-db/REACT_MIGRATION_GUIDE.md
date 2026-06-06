# React UI Migration Guide

## Overview

This guide covers the refactoring of the Mortgage Graph Platform from a Streamlit UI to a production-grade React + TypeScript single-page application (SPA).

## Architecture Summary

### New Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Material-UI (component library)
- React Query (server state management)
- Zustand (client state management)
- Cytoscape.js (graph visualization)
- Axios (HTTP client)

**Backend:**
- FastAPI (existing, enhanced)
- New UI-specific endpoints
- CORS configuration
- Rate limiting (optional)

## Migration Phases

### Phase 1: Development & Parallel Running (Weeks 1-2)

**Goal**: Build React frontend, run alongside Streamlit for validation

**Steps:**

1. **Setup Frontend Environment**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Update .env.local with local API URL
   npm run dev
   ```

2. **Run Existing Streamlit**
   ```bash
   streamlit run app/ui/streamlit_app.py
   ```

3. **Access Both UIs**
   - React (dev): http://localhost:5173
   - Streamlit: http://localhost:8501
   - FastAPI: http://localhost:8000

4. **Test Feature Parity**
   - Create test matrix for each feature
   - Compare behavior between Streamlit and React
   - Document any discrepancies

**Key Files Created:**
- `frontend/src/` — Complete React application
- `app/api/routes_enhanced.py` — New endpoints for React UI

### Phase 2: Feature Freeze & Stabilization (Weeks 3-4)

**Goal**: Stabilize React implementation, fix bugs, add missing features

**Activities:**

1. **Backend Enhancements**
   - Merge `routes_enhanced.py` into `routes.py`
   - Add CORS middleware to FastAPI
   - Test all new endpoints
   - Add rate limiting if needed

2. **Frontend Stabilization**
   - Fix integration bugs
   - Improve error handling
   - Add loading states
   - Test on multiple browsers

3. **Deprecation Planning**
   - Add banner to Streamlit: "This UI is deprecated. Please use the new React app."
   - Document the new UI in README
   - Create runbooks for operators

**Implementation:**

Replace `app/main.py` to add CORS and new routes:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_enhanced import router as enhanced_router
from app.config.logging import configure_logging
from app.config.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.project_name, version="0.1.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Dev
        "http://localhost:80",    # Prod
        "http://localhost",
        # Add production domain in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include enhanced routes (replaces old routes)
app.include_router(enhanced_router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

### Phase 3: Cutover to React (Week 5)

**Decision Point:**
- Is React frontend feature-complete?
- Are all critical bugs fixed?
- Is performance acceptable?

**If YES, Proceed:**

1. **Update Docker Compose**
   ```yaml
   version: '3.8'
   services:
     neo4j:
       # ... existing config
       
     api:
       # ... existing config
       
     frontend:
       build:
         context: .
         dockerfile: Dockerfile.prod
       ports:
         - "80:80"
       depends_on:
         - api
   ```

2. **Build Production Frontend**
   ```bash
   cd frontend
   npm run build
   # Output: dist/ folder
   ```

3. **Update README**
   - Replace Streamlit instructions with React UI
   - Point to http://localhost:80 for production UI
   - Keep Streamlit instructions in a "Legacy UI" section

4. **Remove Streamlit Service**
   - Delete `app/ui/streamlit_app.py`
   - Remove `streamlit>=1.43.0` from `requirements.txt`
   - Update `docker-compose.yml` to remove Streamlit service

5. **Tag Release**
   ```bash
   git tag -a v0.2.0 -m "Migrate UI from Streamlit to React"
   git push origin v0.2.0
   ```

**If NO, Extend Parallel Running:**
- Continue development and fixes
- Schedule cutover for following week
- Keep both UIs available

### Phase 4: Post-Migration Optimization (Weeks 6+)

**Activities:**

1. **WebSocket Integration** (Real-time Job Progress)
   ```python
   # In FastAPI
   from fastapi import WebSocket
   
   @app.websocket("/ws/jobs/{job_id}")
   async def websocket_job_status(websocket: WebSocket, job_id: str):
       await websocket.accept()
       # Stream job progress updates
   ```

   ```typescript
   // In React
   const useJobProgress = (jobId: string) => {
     const [progress, setProgress] = useState(0);
     
     useEffect(() => {
       const ws = new WebSocket(`ws://localhost:8000/ws/jobs/${jobId}`);
       ws.onmessage = (e) => {
         const data = JSON.parse(e.data);
         setProgress(data.progress);
       };
     }, [jobId]);
   };
   ```

2. **RBAC Implementation**
   - Implement JWT/OIDC auth
   - Add role-based access control
   - Restrict endpoints by role

3. **Performance Monitoring**
   - Add Sentry error tracking
   - Monitor Core Web Vitals
   - Set up APM (Application Performance Monitoring)

4. **Theming**
   - Add dark mode support
   - Customize colors and fonts
   - Persist theme preference

## Deployment Strategies

### Strategy 1: Docker (Recommended)

**Single Container (Frontend + Backend + Nginx)**

```dockerfile
# Dockerfile.prod (multi-stage)

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci --only=production && npm run build

# Stage 2: Build Python
FROM python:3.11-slim AS backend-builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 3: Runtime
FROM python:3.11-slim
WORKDIR /app

# Copy Python deps and app
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY app ./app
COPY cypher ./cypher
COPY scripts ./scripts

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Install Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Configure Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 80 8000

# Startup script
CMD ["sh", "-c", "nginx -g 'daemon off;' & exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

**Nginx Configuration** (`nginx.conf`):

```nginx
upstream api {
    server localhost:8000;
}

server {
    listen 80;
    server_name _;

    # Frontend SPA
    location / {
        root /app/frontend/dist;
        try_files $uri /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support (for job progress)
    location /ws {
        proxy_pass http://api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;
}
```

**Build and Run:**

```bash
docker build -f Dockerfile.prod -t mortgage-graph-ui .
docker run -p 80:8000 -e NEO4J_URI=bolt://neo4j:7687 mortgage-graph-ui
```

### Strategy 2: Separate Services

**Recommended for High-Scale Deployments**

```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.26
    # ... config

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - neo4j

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"  # or 3000 if using Node server
    depends_on:
      - api
    environment:
      - VITE_API_BASE_URL=http://api:8000

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - frontend
      - api
```

### Strategy 3: Kubernetes (Enterprise)

**Helm Chart Values** (`values.yaml`):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mortgage-graph-config
data:
  API_BASE_URL: "http://api:8000"
  NEO4J_URI: "bolt://neo4j:7687"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mortgage-graph-api
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: api
        image: mortgage-graph:latest
        ports:
        - containerPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mortgage-graph-frontend
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: frontend
        image: mortgage-graph-frontend:latest
        ports:
        - containerPort: 80
```

## Environment Configuration

### Development

**`frontend/.env.local`:**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_GRAPH_EXPLORER=true
VITE_ENABLE_JOB_MONITOR=true
VITE_ENABLE_RBAC=false
```

**`backend/.env`:**
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme123
ENV=dev
```

### Production

**`frontend/.env.prod`:**
```env
VITE_API_BASE_URL=https://api.mortgage-graph.com
VITE_ENABLE_GRAPH_EXPLORER=true
VITE_ENABLE_JOB_MONITOR=true
VITE_ENABLE_RBAC=true
VITE_SENTRY_DSN=https://...
```

**`backend/.env.prod`:**
```env
NEO4J_URI=bolt+s://production-neo4j:7687
NEO4J_USER=${NEO4J_USER_PROD}
NEO4J_PASSWORD=${NEO4J_PASSWORD_PROD}
ENV=production
LOG_LEVEL=WARN
```

## Testing Checklist

Before deploying to production:

### Frontend
- [ ] All pages load without errors
- [ ] Form validation works as expected
- [ ] API errors display appropriate messages
- [ ] Tables paginate correctly
- [ ] Graph explorer executes queries
- [ ] Job monitor refreshes automatically
- [ ] Dashboard metrics update
- [ ] Mobile/responsive view works
- [ ] Accessibility (keyboard navigation, screen readers)
- [ ] Performance: Core Web Vitals < 3s LCP, 100ms FID

### Backend
- [ ] All new endpoints return correct data
- [ ] Error responses match expected format
- [ ] Rate limiting works
- [ ] CORS headers set correctly
- [ ] Neo4j connection retries on failure
- [ ] Postgres fallback works (if enabled)

### Integration
- [ ] React frontend communicates with FastAPI correctly
- [ ] Form submissions ingest loans
- [ ] Risk queries return consistent results in both UIs (if parallel)
- [ ] Graph queries execute and return results
- [ ] Job management endpoints work

## Rollback Plan

If critical issues arise:

1. **Immediate**: Revert Nginx config to serve Streamlit
   ```bash
   git revert <commit-hash>
   docker-compose down
   docker-compose up -d
   ```

2. **Communicate**: Notify users of revert
   ```
   The React UI has been temporarily disabled due to critical issues.
   The Streamlit UI is available at [URL].
   We are investigating and will restore React UI shortly.
   ```

3. **Root Cause Analysis**: Debug the issue
   - Check error logs (frontend: browser console, backend: app logs)
   - Verify database connectivity
   - Review recent code changes

4. **Re-deploy**: Fix issue, test, and deploy again

## Documentation Updates

### Update README.md

**Before:**
```markdown
## Streamlit UI
```bash
streamlit run app/ui/streamlit_app.py
```
```

**After:**
```markdown
## React UI

The application includes a modern React + TypeScript frontend built with Material-UI.

### Development
```bash
cd frontend
npm install
npm run dev
```
Visit http://localhost:5173

### Production
See Docker Compose section below.

## Legacy Streamlit UI (Deprecated)
[Move old instructions here]
```

### Update docker-compose.yml

Replace Streamlit service with frontend:

```yaml
frontend:
  build:
    context: .
    dockerfile: Dockerfile.prod
  ports:
    - "80:80"
  depends_on:
    - api
  environment:
    - VITE_API_BASE_URL=http://api:8000
```

## Support & Troubleshooting

### Common Issues

**Issue**: React frontend can't reach API
- **Check**: CORS headers in FastAPI
- **Solution**: Ensure `allow_origins` includes frontend domain

**Issue**: Graph queries timeout
- **Check**: Cypher query complexity
- **Solution**: Add `LIMIT` clause, optimize indexes in Neo4j

**Issue**: Form validation fails silently
- **Check**: Browser console for JavaScript errors
- **Solution**: Ensure Zod schema matches backend Pydantic model

### Getting Help

- Check [CLAUDE.md](CLAUDE.md) for development setup
- Review component stories in Storybook (if added)
- Check API logs: `docker-compose logs api`
- Check browser console: F12 → Console tab

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Development | Weeks 1-2 | React app complete, parallel testing |
| Stabilization | Weeks 3-4 | Bug fixes, backend enhancements, docs |
| Cutover | Week 5 | Production deployment, Streamlit deprecation |
| Optimization | Weeks 6+ | WebSocket, RBAC, monitoring |

## Conclusion

This migration modernizes the Mortgage Graph Platform with a production-grade React UI while maintaining the robust FastAPI backend. The phased approach ensures a safe, well-tested transition with minimal user impact.

For questions or issues, refer to the development team or create an issue in the repository.
