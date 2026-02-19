"""OAuth2 dependencies for FastAPI."""

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.services.oauth2_service import OAuth2Service
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class OAuth2Dependencies:
    """Container for managing OAuth2-related dependencies."""

    @staticmethod
    async def verify_oauth2_token(token: str = Depends(oauth2_scheme)) -> str:
        """
        Dependency to verify OAuth2 JWT token.
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            The user email (subject) from the token
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        oauth_service = OAuth2Service()
        token_data = oauth_service.verify_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return token_data


verify_oauth2_token = OAuth2Dependencies.verify_oauth2_token
get_current_user = verify_oauth2_token
