from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_simple import router
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

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
