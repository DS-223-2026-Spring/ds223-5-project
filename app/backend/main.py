from fastapi import FastAPI
from core.config import settings
from api.api import api_router
from db.connection import health_check

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API"}

@app.get("/health")
def health():
    # check database connectivity
    db_ok = health_check()
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
    }
