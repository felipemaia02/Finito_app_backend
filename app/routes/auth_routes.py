"""Authentication routes with class-based views using fastapi-utils."""

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi_utils.cbv import cbv

from app.controllers.auth_controller import AuthController
from app.infrastructure.dependencies.auth_controller_dependencies import (
    AuthDependencies,
)
from app.infrastructure.dependencies.oauth2_dependencies import verify_oauth2_token
from app.infrastructure.dependencies.auth_dependencies import verify_api_key
from app.models.auth_schema import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    TokenValidationResponse,
    TokenData,
)
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(tags=["authentication"], prefix="/auth")


@cbv(router)
class AuthViews:
    """Class-based views for authentication operations."""

    controller: AuthController = Depends(AuthDependencies.get_controller)
    api_key: str = Security(verify_api_key)

    @router.post(
        "/login",
        response_model=TokenResponse,
        status_code=status.HTTP_200_OK,
    )
    async def login(self, login_data: LoginRequest) -> TokenResponse:
        """
        Authenticate user with email and password.
        Returns JWT access token and refresh token for subsequent API calls.

        Args:
            login_data: Email and password credentials

        Returns:
            TokenResponse with JWT access and refresh tokens

        Raises:
            HTTPException: If credentials are invalid
        """
        try:
            return await self.controller.login(login_data)
        except ValueError as ve:
            error_msg = str(ve)
            if error_msg.startswith("EMAIL_NOT_VERIFIED:"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_msg.removeprefix("EMAIL_NOT_VERIFIED: "),
                )
            logger.error(f"Login validation error: {ve}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg
            )
        except Exception as e:
            logger.error(f"Error logging in: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error logging in: {str(e)}",
            )

    @router.post(
        "/refresh",
        response_model=TokenResponse,
        status_code=status.HTTP_200_OK,
    )
    async def refresh_token(self, request: RefreshTokenRequest) -> TokenResponse:
        """
        Refresh an expired access token using a refresh token.

        Args:
            request: RefreshTokenRequest with refresh token

        Returns:
            TokenResponse with new JWT tokens

        Raises:
            HTTPException: If refresh token is invalid or expired
        """
        try:
            return await self.controller.refresh_token(request)
        except ValueError as ve:
            logger.error(f"Refresh token validation error: {ve}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error refreshing token: {str(e)}",
            )

    @router.post(
        "/validate",
        response_model=TokenValidationResponse,
        status_code=status.HTTP_200_OK,
    )
    async def validate_token(
        self, current_user: TokenData = Security(verify_oauth2_token)
    ) -> TokenValidationResponse:
        """
        Validate the access token.

        Args:
            current_user: Extracted from valid access token via Security dependency

        Returns:
            TokenValidationResponse indicating token is valid
        """
        try:
            logger.info(f"Token validated for user: {current_user.sub}")
            return TokenValidationResponse(
                valid=True, email=current_user.sub, expires_at=current_user.exp
            )
        except Exception as e:  # pragma: no cover
            logger.error(f"Error validating token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error validating token: {str(e)}",
            )
