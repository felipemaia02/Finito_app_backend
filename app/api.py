"""
FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.infrastructure.settings import get_settings
from app.infrastructure.database import Database
from app.routes.expense_routes import router as expense_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Startup: Initialize database connection
    Shutdown: Close database connection
    """
    await Database.connect()
    yield
    await Database.disconnect()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expense_router)


@app.get("/")
async def health_check():
    """Root endpoint - Health check"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version
    }
