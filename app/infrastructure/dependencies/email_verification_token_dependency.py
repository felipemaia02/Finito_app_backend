"""Dependency for validating email-verification JWTs."""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.oauth2_service import OAuth2Service
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

_bearer_scheme = HTTPBearer()


async def verify_verification_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """
    Extract and validate the short-lived email-verification JWT.

    Returns:
        user_id string from the token payload

    Raises:
        HTTPException 401: If the token is missing, expired, or of the wrong type
    """
    oauth_service = OAuth2Service()
    user_id = oauth_service.verify_verification_token(credentials.credentials)

    if user_id is None:
        logger.warning("Invalid or expired verification token presented")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired verification token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
