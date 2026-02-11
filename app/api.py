"""
FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.infrastructure.settings import get_settings
from app.infrastructure.database import Database
from app.infrastructure.logger import get_logger
from app.routes.expense_routes import router as expense_router

settings = get_settings()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Startup: Initialize database connection
    Shutdown: Close database connection
    """
    logger.info("Application startup - Initializing database connection")
    await Database.connect()
    logger.info("Application startup - Database connected successfully")
    yield
    logger.info("Application shutdown - Disconnecting from database")
    await Database.disconnect()
    logger.info("Application shutdown - Database disconnected successfully")


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


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Health check: root endpoint accessed")
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - verifies database connectivity"""
    try:
        logger.info("Health check: verifying database connection")
        
        if not Database.is_connected():
            logger.warning("Health check: database not connected yet")
            return {
                "status": "initializing",
                "database": "connecting"
            }
        
        db = Database.get_db()
        await db.command('ping')

        logger.info("Health check: all systems operational")
        return {
            "status": "ok",
            "database": "connected",
            "message": f"{settings.app_name} is healthy"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }, 503