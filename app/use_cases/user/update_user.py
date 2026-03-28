"""Update User use case."""

from typing import Optional
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.dtos.user_dtos import UpdateUserInput
from app.models.user_schema import UserResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class UpdateUserUseCase(IUseCase[UpdateUserInput, Optional[UserResponse]]):
    """Use case for updating user information."""

    def __init__(self, repository: IUserRepository):
        """
        Initialize the use case with a repository dependency.

        Args:
            repository: Implementation of IUserRepository
        """
        self.repository = repository

    async def execute(self, input_data: UpdateUserInput) -> Optional[UserResponse]:
        """
        Update user information.

        Args:
            input_data: UpdateUserInput with user ID and update data

        Returns:
            Updated UserResponse if user found, None otherwise

        Raises:
            ValueError: If new email already exists
            Exception: If database operation fails
        """
        try:
            logger.info(f"Updating user with ID: {input_data.user_id}")

            existing_user = await self.repository.get_by_id(input_data.user_id)
            if not existing_user:
                logger.warning(f"User not found with ID: {input_data.user_id}")
                return None

            if (
                input_data.user_data.email
                and input_data.user_data.email != existing_user.email
            ):
                existing_email_user = await self.repository.get_by_email(
                    input_data.user_data.email
                )
                if existing_email_user:
                    logger.warning(f"Email {input_data.user_data.email} already exists")
                    raise ValueError(
                        f"Email {input_data.user_data.email} is already registered"
                    )

            update_data = input_data.user_data.model_dump(exclude_unset=True)

            if "email" in update_data and update_data["email"]:
                update_data["email"] = update_data["email"].lower()

            for key, value in update_data.items():
                if value is not None:
                    setattr(existing_user, key, value)

            existing_user.update_timestamp()

            updated_user = await self.repository.update(
                input_data.user_id, existing_user
            )

            if updated_user:
                logger.info(f"User updated successfully with ID: {input_data.user_id}")
                return UserResponse(**updated_user.model_dump())

            return None
        except ValueError as ve:
            logger.warning(f"Validation error updating user: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error updating user with ID {input_data.user_id}: {e}")
            raise
