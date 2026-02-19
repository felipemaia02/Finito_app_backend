"""API Key authentication service implementation."""

from app.domain.interfaces.auth_interface import IAuthService
from app.infrastructure.settings import get_settings
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class APIKeyAuthService(IAuthService):
    """Service for validating API keys."""

    def __init__(self):
        """Initialize the service with application settings."""
        self.settings = get_settings()

    async def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key by comparing with settings.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            True if the key matches settings.api_key, False otherwise
        """
        is_valid = api_key == self.settings.api_key

        if not is_valid:
            logger.warning("API key validation failed")
        
        logger.info("API key validation completed")

        return is_valid
