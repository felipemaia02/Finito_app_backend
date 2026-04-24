"""Dependency injection container for email verification operations."""

from fastapi import Depends

from app.controllers.email_verification_controller import EmailVerificationController
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.interfaces.email_service_interface import IEmailService
from app.infrastructure.repositories.email_verification_repository import (
    MongoEmailVerificationRepository,
)
from app.infrastructure.repositories.user_repository import MongoUserRepository
from app.services.resend_email_service import ResendEmailService


class EmailVerificationDependencies:
    """Container for managing email verification dependencies."""

    @staticmethod
    def get_verification_repository() -> IEmailVerificationRepository:
        return MongoEmailVerificationRepository()

    @staticmethod
    def get_user_repository() -> IUserRepository:
        return MongoUserRepository()

    @staticmethod
    def get_email_service() -> IEmailService:
        return ResendEmailService()

    @staticmethod
    def get_controller(
        user_repository: IUserRepository = Depends(get_user_repository.__func__),
        verification_repository: IEmailVerificationRepository = Depends(
            get_verification_repository.__func__
        ),
        email_service: IEmailService = Depends(get_email_service.__func__),
    ) -> EmailVerificationController:
        return EmailVerificationController(
            user_repository, verification_repository, email_service
        )
