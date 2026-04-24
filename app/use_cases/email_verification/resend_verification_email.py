"""Resend verification email use case."""

from app.domain.interfaces.use_case import IUseCase
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.interfaces.email_service_interface import IEmailService
from app.domain.dtos.email_verification_dtos import (
    ResendVerificationEmailInput,
    SendVerificationEmailInput,
)
from app.models.response_schema import StandardResponse
from app.use_cases.email_verification.send_verification_email import (
    SendVerificationEmailUseCase,
)
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

_MAX_RESENDS = 3


class ResendVerificationEmailUseCase(
    IUseCase[ResendVerificationEmailInput, StandardResponse]
):
    """
    Invalidates the current token and sends a fresh verification code.
    Limited to 3 resends per registration.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IEmailVerificationRepository,
        email_service: IEmailService,
    ):
        self.user_repository = user_repository
        self.verification_repository = verification_repository
        self.email_service = email_service

    async def execute(
        self, input_data: ResendVerificationEmailInput
    ) -> StandardResponse:
        """
        Args:
            input_data: ResendVerificationEmailInput(user_id)

        Returns:
            StandardResponse confirming the email was sent

        Raises:
            ValueError: If user not found, already verified, or resend limit exceeded
            Exception: On infrastructure failures
        """
        try:
            logger.info(
                f"Resend verification email requested for user_id={input_data.user_id}"
            )

            user = await self.user_repository.get_by_id_unverified(input_data.user_id)
            if user is None:
                raise ValueError("User not found.")

            if user.is_email_verified:
                raise ValueError("Email is already verified.")

            # Check resend limit from latest token
            latest = await self.verification_repository.get_latest_by_user_id(
                input_data.user_id
            )
            current_resend_count = latest.resend_count if latest else 0

            if current_resend_count >= _MAX_RESENDS:
                logger.warning(
                    f"Resend limit reached for user_id={input_data.user_id}"
                )
                raise ValueError(
                    "Maximum number of verification email resends reached. "
                    "Please contact support."
                )

            send_use_case = SendVerificationEmailUseCase(
                self.verification_repository, self.email_service
            )
            await send_use_case.execute(
                SendVerificationEmailInput(
                    user_id=input_data.user_id,
                    email=str(user.email),
                )
            )

            logger.info(
                f"Verification email resent for user_id={input_data.user_id}"
            )
            return StandardResponse(
                message="Verification email sent. Please check your inbox."
            )

        except ValueError as ve:
            logger.warning(f"Validation error on resend: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error resending verification email: {e}")
            raise
