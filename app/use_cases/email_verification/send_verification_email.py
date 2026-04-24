"""Send verification email use case."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.domain.interfaces.use_case import IUseCase
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.interfaces.email_service_interface import IEmailService
from app.domain.entities.email_verification_token_entity import EmailVerificationToken
from app.domain.dtos.email_verification_dtos import SendVerificationEmailInput
from app.services.oauth2_service import OAuth2Service
from app.infrastructure.logger import get_logger
from app.infrastructure.settings import get_settings

logger = get_logger(__name__)

_CODE_TTL_MINUTES = 15
_MAX_RESENDS = 3


class SendVerificationEmailUseCase(
    IUseCase[SendVerificationEmailInput, str]
):
    """
    Generates a 6-digit code, persists its SHA-256 hash, sends the email,
    and returns a short-lived JWT verification token (carries user_id only).
    """

    def __init__(
        self,
        verification_repository: IEmailVerificationRepository,
        email_service: IEmailService,
    ):
        self.verification_repository = verification_repository
        self.email_service = email_service
        self.settings = get_settings()

    async def execute(self, input_data: SendVerificationEmailInput) -> str:
        """
        Args:
            input_data: SendVerificationEmailInput(user_id, email)

        Returns:
            Encoded JWT verification token (type=email_verification)

        Raises:
            ValueError: If the resend limit has been reached
            Exception: On infrastructure failures
        """
        try:
            logger.info(f"Sending verification email for user_id={input_data.user_id}")

            # Determine current resend_count from the latest existing token
            resend_count = 0
            latest = await self.verification_repository.get_latest_by_user_id(
                input_data.user_id
            )
            if latest is not None:
                resend_count = latest.resend_count

            if resend_count >= _MAX_RESENDS:
                logger.warning(
                    f"Resend limit reached for user_id={input_data.user_id}"
                )
                raise ValueError(
                    "Maximum number of verification email resends reached. "
                    "Please contact support."
                )

            # Invalidate any previous active tokens
            await self.verification_repository.invalidate_all_by_user_id(
                input_data.user_id
            )

            # Generate 6-digit code and hash it
            code = str(secrets.randbelow(900000) + 100000)  # [100000, 999999]
            code_hash = hashlib.sha256(code.encode()).hexdigest()

            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=_CODE_TTL_MINUTES
            )

            token_entity = EmailVerificationToken(
                user_id=input_data.user_id,
                code_hash=code_hash,
                expires_at=expires_at,
                resend_count=resend_count,
            )
            await self.verification_repository.create(token_entity)

            # Send the plain-text code via email
            await self.email_service.send_verification_email(
                to_email=input_data.email, code=code
            )

            # Build short-lived JWT
            oauth_service = OAuth2Service()
            verification_token = oauth_service.create_verification_token(
                user_id=input_data.user_id
            )

            logger.info(
                f"Verification email sent and token issued for user_id={input_data.user_id}"
            )
            return verification_token

        except ValueError as ve:
            logger.warning(f"Validation error sending verification email: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            raise
