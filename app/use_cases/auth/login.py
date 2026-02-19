"""Login use case for user authentication."""

from app.models.auth_schema import LoginRequest, TokenResponse
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.services.oauth2_service import OAuth2Service
from app.infrastructure.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


class LoginUseCase:
    """Use case for authenticating users."""
    
    def __init__(self, repository: IUserRepository):
        """
        Initialize the use case with repository dependency.
        
        Args:
            repository: Implementation of IUserRepository
        """
        self.repository = repository
        self.oauth_service = OAuth2Service()
    
    async def execute(self, login_data: LoginRequest) -> TokenResponse:
        """
        Authenticate user with email and password.
        
        Args:
            login_data: LoginRequest schema with email and password
            
        Returns:
            TokenResponse with JWT access token and refresh token
            
        Raises:
            ValueError: If email not found or password is incorrect
        """
        try:
            logger.info(f"Login attempt for email: {login_data.email}")
            
            # Get user by email
            user = await self.repository.get_by_email(login_data.email)
            
            if not user:
                logger.warning(f"Login failed: User not found with email {login_data.email}")
                raise ValueError("Invalid email or password")
            
            # Create token pair
            access_token, refresh_token, expires_at = self.oauth_service.create_token_pair(user.email)
            
            # Calculate expires_in in seconds
            expires_in = int((expires_at - datetime.utcnow()).total_seconds())
            
            logger.info(f"Login successful for email: {login_data.email}")
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=expires_in,
                expires_at=expires_at
            )
            
        except ValueError as ve:
            logger.error(f"Validation error during login: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise
