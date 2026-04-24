"""Email verification routes."""

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi_utils.cbv import cbv

from app.controllers.email_verification_controller import EmailVerificationController
from app.infrastructure.dependencies.email_verification_dependencies import (
    EmailVerificationDependencies,
)
from app.infrastructure.dependencies.email_verification_token_dependency import (
    verify_verification_token,
)
from app.infrastructure.dependencies.auth_dependencies import verify_api_key
from app.models.email_verification_schema import (
    VerifyEmailRequest,
    UserRegisterResponse,
    RequestVerificationRequest,
)
from app.models.auth_schema import TokenResponse
from app.models.response_schema import StandardResponse
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["email-verification"], prefix="/auth")


@cbv(router)
class EmailVerificationViews:
    """Class-based views for email verification operations."""

    controller: EmailVerificationController = Depends(
        EmailVerificationDependencies.get_controller
    )
    api_key: str = Security(verify_api_key)

    @router.post(
        "/verify-email",
        response_model=TokenResponse,
        status_code=status.HTTP_200_OK,
        summary="Verify email with code",
        description=(
            "Submit the 6-digit code received by email. "
            "Requires the short-lived verification JWT issued at registration "
            "in the Authorization: Bearer header."
        ),
    )
    async def verify_email(
        self,
        body: VerifyEmailRequest,
        user_id: str = Depends(verify_verification_token),
    ) -> TokenResponse:
        """Validate the code and activate the user account."""
        try:
            return await self.controller.verify_email(
                user_id=user_id, code=body.code
            )
        except ValueError as ve:
            logger.warning(f"Email verification failed: {ve}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )

    @router.post(
        "/resend-verification",
        response_model=StandardResponse,
        status_code=status.HTTP_200_OK,
        summary="Resend verification email",
        description=(
            "Request a new 6-digit code. Limited to 3 resends. "
            "Requires the verification JWT in the Authorization: Bearer header."
        ),
    )
    async def resend_verification(
        self,
        user_id: str = Depends(verify_verification_token),
    ) -> StandardResponse:
        """Invalidate the current code and send a fresh one."""
        try:
            return await self.controller.resend_verification(user_id=user_id)
        except ValueError as ve:
            logger.warning(f"Resend verification failed: {ve}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error resending verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )

    @router.post(
        "/request-verification",
        response_model=UserRegisterResponse,
        status_code=status.HTTP_200_OK,
        summary="Request a new verification email",
        description=(
            "Allows a registered but unverified user to request a fresh 6-digit code "
            "when the original verification token has expired. "
            "Only requires the API Key — no Bearer token needed."
        ),
    )
    async def request_verification(
        self,
        body: RequestVerificationRequest,
    ) -> UserRegisterResponse:
        """Send a new verification code to an unverified email address."""
        try:
            return await self.controller.request_verification(email=str(body.email))
        except ValueError as ve:
            logger.warning(f"Request verification failed: {ve}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error requesting verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )
