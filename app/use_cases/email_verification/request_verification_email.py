"""Request a new verification email use case.

Used when a previously registered but unverified user needs a fresh code,
for example because the original verification token expired.
"""

from app.domain.interfaces.use_case import IUseCase
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.interfaces.email_service_interface import IEmailService
from app.domain.dtos.email_verification_dtos import (
    RequestVerificationInput,
    SendVerificationEmailInput,
)
from app.models.email_verification_schema import UserRegisterResponse
from app.use_cases.email_verification.send_verification_email import (
    SendVerificationEmailUseCase,
)
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class RequestVerificationEmailUseCase(
    IUseCase[RequestVerificationInput, UserRegisterResponse]
):
    """
    Allows an already-registered but unverified user to request a fresh
    verification code by supplying their email address.
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
        self, input_data: RequestVerificationInput
    ) -> UserRegisterResponse:
        """
        Returns the same generic response regardless of whether the email
        exists, is already verified, or the resend limit was reached.
        This prevents email enumeration and abuse.

        Raises:
            Exception: Only on unexpected infrastructure failures
        """
        _GENERIC_RESPONSE = UserRegisterResponse(
            message="If this email is registered and unverified, a code has been sent.",
            verification_token="",
        )
        try:
            logger.info(
                f"Verification request received for email={input_data.email}"
            )

            user = await self.user_repository.get_by_email_unverified(
                input_data.email
            )
            if user is None:
                logger.info(
                    f"Request-verification: email not found (silent) email={input_data.email}"
                )
                return _GENERIC_RESPONSE

            if user.is_email_verified:
                logger.info(
                    f"Request-verification: already verified (silent) user_id={user.id}"
                )
                return _GENERIC_RESPONSE

            send_use_case = SendVerificationEmailUseCase(
                self.verification_repository, self.email_service
            )
            try:
                verification_token = await send_use_case.execute(
                    SendVerificationEmailInput(
                        user_id=str(user.id),
                        email=str(user.email),
                    )
                )
            except ValueError:
                # Resend limit reached — do not reveal this to the caller
                logger.info(
                    f"Request-verification: resend limit reached (silent) user_id={user.id}"
                )
                return _GENERIC_RESPONSE

            logger.info(
                f"New verification email sent for user_id={user.id}"
            )
            return UserRegisterResponse(
                message="If this email is registered and unverified, a code has been sent.",
                verification_token=verification_token,
            )

        except Exception as e:
            logger.error(f"Error on request-verification: {e}")
            raise
