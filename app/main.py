from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import engine
from app import models
from app.routers import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    # Shutdown logic (optional)

app = FastAPI(
    title="User CRUD API",
    description="A simple CRUD API for user management",
    version="1.0.0",
    lifespan=lifespan,
)

# Include user router with API version prefix
app.include_router(users.router, prefix="/api/v1")

@app.get("/")
async def root():
    """
    Welcome endpoint for quick testing.
    """
    return {"message": "Welcome to User CRUD API"}

@app.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    """
    return {"status": "healthy"}
