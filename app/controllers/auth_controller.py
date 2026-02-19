"""
Authentication controller for handling HTTP coordination and delegating to use cases.
"""

from app.domain.interfaces.user_repository_interface import IUserRepository
from app.models.auth_schema import LoginRequest, TokenResponse, RefreshTokenRequest
from app.use_cases.auth.login import LoginUseCase
from app.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class AuthController:
    """
    Controller for authentication operations.
    Coordinates between API routes and the auth use case layer.
    Acts as a thin HTTP coordination layer.
    """
    
    def __init__(self, repository: IUserRepository):
        """
        Initialize the controller with a repository dependency.
        Creates use case instances for dependency injection.
        
        Args:
            repository: Implementation of IUserRepository
        """
        logger.info("Initializing AuthController")
        self.repository = repository
        self.login_use_case = LoginUseCase(repository)
        self.refresh_token_use_case = RefreshTokenUseCase()
        logger.info("AuthController initialized successfully")
    
    async def login(self, login_data: LoginRequest) -> TokenResponse:
        """
        Authenticate user with email and password.
        Delegates to LoginUseCase.
        
        Args:
            login_data: LoginRequest schema with email and password
            
        Returns:
            TokenResponse with JWT access token and refresh token
            
        Raises:
            ValueError: If email not found or password is incorrect
            Exception: If database operation fails
        """
        try:
            logger.info(f"Login attempt for email: {login_data.email}")
            return await self.login_use_case.execute(login_data)
        except Exception as e:
            logger.error(f"Error logging in: {e}")
            raise
    
    async def refresh_token(self, refresh_data: RefreshTokenRequest) -> TokenResponse:
        """
        Refresh an expired access token.
        Delegates to RefreshTokenUseCase.
        
        Args:
            refresh_data: RefreshTokenRequest schema with refresh token
            
        Returns:
            TokenResponse with new JWT access token
            
        Raises:
            ValueError: If refresh token is invalid or expired
            Exception: If token operation fails
        """
        try:
            logger.info("Refresh token attempt")
            return await self.refresh_token_use_case.execute(refresh_data.refresh_token)
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
