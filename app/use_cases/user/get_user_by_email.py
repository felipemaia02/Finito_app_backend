"""Get User by Email use case."""

from typing import Optional
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.dtos.user_dtos import GetUserByEmailInput
from app.models.user_schema import UserResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class GetUserByEmailUseCase(IUseCase[GetUserByEmailInput, Optional[UserResponse]]):
    """Use case for retrieving a user by their email address."""

    def __init__(self, repository: IUserRepository):
        """
        Initialize the use case with a repository dependency.

        Args:
            repository: Implementation of IUserRepository
        """
        self.repository = repository

    async def execute(self, input_data: GetUserByEmailInput) -> Optional[UserResponse]:
        """
        Get a user by their email address.

        Args:
            input_data: Email address to search for

        Returns:
            UserResponse if user found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Retrieving user with email: {input_data.email}")

            user = await self.repository.get_by_email(input_data.email)

            if user:
                logger.info(f"User found with email: {input_data.email}")
                return UserResponse(**user.model_dump())

            logger.warning(f"User not found with email: {input_data.email}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user with email {input_data.email}: {e}")
            raise
