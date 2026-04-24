"""Refresh token use case for token renewal."""

from app.models.auth_schema import TokenResponse
from app.services.oauth2_service import OAuth2Service
from app.infrastructure.logger import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)


class RefreshTokenUseCase:
    """Use case for refreshing JWT tokens."""

    def __init__(self):
        """Initialize the use case."""
        self.oauth_service = OAuth2Service()

    async def execute(self, refresh_token: str) -> TokenResponse:
        """
        Refresh an expired access token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            TokenResponse with new JWT access token

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        try:
            logger.info("Refresh token attempt")

            token_data = self.oauth_service.verify_token(
                refresh_token, token_type="refresh"
            )

            if not token_data:
                logger.warning("Refresh token validation failed")
                raise ValueError("Invalid or expired refresh token")

            # Create new token pair
            access_token, new_refresh_token, expires_at = (
                self.oauth_service.create_token_pair(token_data.sub, user_id=token_data.user_id)
            )

            # Calculate expires_in in seconds
            expires_in = int((expires_at - datetime.now(timezone.utc)).total_seconds())

            logger.info(f"Token refreshed successfully for email: {token_data.sub}")
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=expires_in,
                expires_at=expires_at,
            )

        except ValueError as ve:
            logger.error(f"Validation error during refresh: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
