from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_enhanced import router
from app.config.logging import configure_logging
from app.config.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Mortgage Graph Platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Enable CORS for all origins (will restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes - MUST be before any catch-all routes
app.include_router(router)

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Mortgage Graph Platform API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
