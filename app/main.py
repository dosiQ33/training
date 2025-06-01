from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import engine
from app import models
from app.routers import users, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    # Shutdown logic (optional)


app = FastAPI(
    title="Training API with Telegram Auth",
    description="A CRUD API with Telegram Web App authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers with API version prefix
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Welcome endpoint
    """
    return {
        "message": "Training Mini App API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "training-mini-app-api"}
