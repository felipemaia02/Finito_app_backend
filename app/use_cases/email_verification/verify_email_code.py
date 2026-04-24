"""Verify email code use case."""

import hashlib
from datetime import datetime, timezone

from app.domain.interfaces.use_case import IUseCase
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.dtos.email_verification_dtos import VerifyEmailCodeInput
from app.models.auth_schema import TokenResponse
from app.services.oauth2_service import OAuth2Service
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

_MAX_ATTEMPTS = 5


class VerifyEmailCodeUseCase(IUseCase[VerifyEmailCodeInput, TokenResponse]):
    """
    Validates the 6-digit code against the stored hash.
    On success: activates the user and returns a full login TokenResponse.
    On failure: increments attempt counter; blocks after 5 failures.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IEmailVerificationRepository,
    ):
        self.user_repository = user_repository
        self.verification_repository = verification_repository

    async def execute(self, input_data: VerifyEmailCodeInput) -> TokenResponse:
        """
        Args:
            input_data: VerifyEmailCodeInput(user_id, code)

        Returns:
            TokenResponse with access + refresh tokens

        Raises:
            ValueError: If code is invalid, expired, or max attempts exceeded
            Exception: On infrastructure failures
        """
        try:
            logger.info(f"Verifying email code for user_id={input_data.user_id}")

            token = await self.verification_repository.get_valid_token_by_user_id(
                input_data.user_id
            )

            if token is None:
                logger.warning(
                    f"No active verification token found for user_id={input_data.user_id}"
                )
                raise ValueError(
                    "No active verification token found. Request a new code."
                )

            # Check expiration
            now = datetime.now(timezone.utc)
            expires_at = token.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if now > expires_at:
                logger.warning(
                    f"Verification token expired for user_id={input_data.user_id}"
                )
                raise ValueError(
                    "Verification code has expired. Request a new one."
                )

            # Check attempt limit
            if token.attempts >= _MAX_ATTEMPTS:
                logger.warning(
                    f"Max attempts reached for user_id={input_data.user_id}"
                )
                raise ValueError(
                    "Too many failed attempts. Request a new verification code."
                )

            # Compare hashes
            submitted_hash = hashlib.sha256(input_data.code.encode()).hexdigest()
            if submitted_hash != token.code_hash:
                await self.verification_repository.increment_attempts(token.id)
                remaining = _MAX_ATTEMPTS - (token.attempts + 1)
                logger.warning(
                    f"Invalid code for user_id={input_data.user_id}. "
                    f"{remaining} attempts remaining."
                )
                raise ValueError(
                    f"Invalid verification code. {remaining} attempts remaining."
                )

            # Mark token as used
            await self.verification_repository.mark_as_used(token.id)

            # Activate user
            user = await self.user_repository.get_by_id_unverified(input_data.user_id)
            if user is None:
                raise ValueError("User not found.")

            user.is_email_verified = True
            user.is_active = True
            user.update_timestamp()
            await self.user_repository.update(user.id, user)

            # Issue login tokens
            oauth_service = OAuth2Service()
            access_token, refresh_token, expires_at_dt = oauth_service.create_token_pair(
                email=str(user.email), user_id=user.id
            )

            expires_in = int((expires_at_dt - datetime.now(timezone.utc)).total_seconds())

            logger.info(
                f"Email verified and user activated for user_id={input_data.user_id}"
            )
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=expires_in,
                expires_at=expires_at_dt,
            )

        except ValueError as ve:
            logger.warning(f"Validation error verifying email: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error verifying email code: {e}")
            raise
