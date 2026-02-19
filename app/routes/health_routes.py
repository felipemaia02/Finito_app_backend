"""Health check routes with class-based views."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from app.infrastructure.logger import get_logger
from app.infrastructure.database import Database
from app.infrastructure.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(tags=["health"])


@cbv(router)
class HealthViews:
    """Class-based views for health check operations."""

    @router.get("/health")
    async def health_check(self):
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
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": str(e)
                }
            )
