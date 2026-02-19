"""
FastAPI application factory
"""
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.infrastructure.settings import get_settings
from app.infrastructure.database.database import Database
from app.infrastructure.logger import get_logger
from app.routes.expense_routes import router as expense_router
from app.routes.user_private_routes import router as user_private_router
from app.routes.user_public_routes import router as user_public_router
from app.routes.auth_routes import router as auth_router
from app.routes.health_routes import router as health_router

settings = get_settings()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Startup: Initialize database connection
    Shutdown: Close database connection
    """
    try:
        logger.info("Application startup - Initializing database connection")
        await Database.connect()
        logger.info("Application startup - Database connected successfully")
        yield
        logger.info("Application shutdown - Disconnecting from database")
        await Database.disconnect()
        logger.info("Application shutdown - Database disconnected successfully")
    except asyncio.exceptions.CancelledError:
        logger.warning("Application lifespan cancelled")   


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

app.include_router(expense_router)
app.include_router(user_public_router)
app.include_router(user_private_router)
app.include_router(auth_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Health check: root endpoint accessed")
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }