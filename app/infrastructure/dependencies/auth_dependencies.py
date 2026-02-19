"""Authentication dependencies for FastAPI."""

from fastapi import Header, HTTPException, status, Depends
from app.services.auth_service import APIKeyAuthService
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class AuthDependencies:
    """Container for managing authentication-related dependencies."""

    _auth_service = APIKeyAuthService()

    @staticmethod
    def get_auth_service() -> APIKeyAuthService:
        """
        Get the authentication service instance.
        
        Returns:
            APIKeyAuthService: Authentication service instance
        """
        return AuthDependencies._auth_service

    @staticmethod
    async def verify_api_key(x_api_key: str = Header(...)) -> str:
        """
        Dependency to verify API key from request header.
        
        Args:
            x_api_key: API key from X-API-Key header (required)
            
        Returns:
            The verified API key
            
        Raises:
            HTTPException: If API key is missing or invalid
        """
        auth_service = AuthDependencies.get_auth_service()
        is_valid = await auth_service.validate_api_key(x_api_key)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return x_api_key


verify_api_key = AuthDependencies.verify_api_key