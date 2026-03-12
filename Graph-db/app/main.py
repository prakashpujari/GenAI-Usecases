from fastapi import FastAPI

from app.api.routes import router
from app.config.logging import configure_logging
from app.config.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.project_name, version="0.1.0")
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
