from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_enhanced import router
from app.config.logging import configure_logging
from app.config.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.project_name, version="0.1.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
        "http://localhost",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:80",
        "https://frontend-qsm5v9hmf-prakash-pujari-s-projects.vercel.app",
        "https://frontend-six-red-29.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include enhanced API routes
app.include_router(router)

# Note: Frontend is served by Vercel, not from this API server
# Static files mount removed to prevent blocking API routes
