"""Email verification controller."""

from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.interfaces.email_service_interface import IEmailService
from app.domain.dtos.email_verification_dtos import (
    VerifyEmailCodeInput,
    ResendVerificationEmailInput,
    RequestVerificationInput,
)
from app.models.auth_schema import TokenResponse
from app.models.response_schema import StandardResponse
from app.models.email_verification_schema import UserRegisterResponse
from app.use_cases.email_verification.verify_email_code import VerifyEmailCodeUseCase
from app.use_cases.email_verification.resend_verification_email import (
    ResendVerificationEmailUseCase,
)
from app.use_cases.email_verification.request_verification_email import (
    RequestVerificationEmailUseCase,
)
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class EmailVerificationController:
    """Thin orchestration layer for email verification operations."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IEmailVerificationRepository,
        email_service: IEmailService,
    ):
        self.verify_use_case = VerifyEmailCodeUseCase(
            user_repository, verification_repository
        )
        self.resend_use_case = ResendVerificationEmailUseCase(
            user_repository, verification_repository, email_service
        )
        self.request_use_case = RequestVerificationEmailUseCase(
            user_repository, verification_repository, email_service
        )

    async def verify_email(
        self, user_id: str, code: str
    ) -> TokenResponse:
        return await self.verify_use_case.execute(
            VerifyEmailCodeInput(user_id=user_id, code=code)
        )

    async def resend_verification(self, user_id: str) -> StandardResponse:
        return await self.resend_use_case.execute(
            ResendVerificationEmailInput(user_id=user_id)
        )

    async def request_verification(self, email: str) -> UserRegisterResponse:
        return await self.request_use_case.execute(
            RequestVerificationInput(email=email)
        )
