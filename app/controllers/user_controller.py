"""
User controller for handling HTTP coordination and delegating to use cases.
"""

from typing import List, Optional
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.models.user_schema import UserCreate, UserUpdate, UserResponse
from app.use_cases.user.create_user import CreateUserUseCase
from app.use_cases.user.get_user_by_id import GetUserByIdUseCase
from app.use_cases.user.get_all_users import GetAllUsersUseCase
from app.use_cases.user.get_user_by_email import GetUserByEmailUseCase
from app.use_cases.user.update_user import UpdateUserUseCase
from app.use_cases.user.delete_user import DeleteUserUseCase
from app.infrastructure.logger import get_logger
from app.domain.dtos.user_dtos import (
    GetAllUsersInput,
    UpdateUserInput,
    GetUserByEmailInput,
)

logger = get_logger(__name__)


class UserController:
    """
    Controller for user operations.
    Coordinates between API routes and the use case layer.
    Acts as a thin HTTP coordination layer.
    """

    def __init__(self, repository: IUserRepository):
        """
        Initialize the controller with a repository dependency.
        Creates use case instances for dependency injection.

        Args:
            repository: Implementation of IUserRepository
        """
        logger.info("Initializing UserController")
        self.repository = repository
        self.create_user_use_case = CreateUserUseCase(repository)
        self.get_user_by_id_use_case = GetUserByIdUseCase(repository)
        self.get_all_users_use_case = GetAllUsersUseCase(repository)
        self.get_user_by_email_use_case = GetUserByEmailUseCase(repository)
        self.update_user_use_case = UpdateUserUseCase(repository)
        self.delete_user_use_case = DeleteUserUseCase(repository)
        logger.info("UserController initialized successfully")

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user in the system.
        Delegates to CreateUserUseCase.

        Args:
            user_data: UserCreate schema with user details

        Returns:
            UserResponse with created user

        Raises:
            ValueError: If email already exists
            Exception: If database operation fails
        """
        try:
            logger.info(f"Registering new user with email: {user_data.email}")
            return await self.create_user_use_case.execute(user_data)
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise

    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """
        Get a user by their ID.
        Delegates to GetUserByIdUseCase.

        Args:
            user_id: User ID to retrieve

        Returns:
            UserResponse if found, None otherwise
        """
        try:
            logger.info(f"Getting user with ID: {user_id}")
            return await self.get_user_by_id_use_case.execute(user_id)
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Get a user by their email address.
        Delegates to GetUserByEmailUseCase.

        Args:
            email: User email to search for

        Returns:
            UserResponse if found, None otherwise
        """
        try:
            logger.info(f"Getting user with email: {email}")
            input_data = GetUserByEmailInput(email=email)
            return await self.get_user_by_email_use_case.execute(input_data)
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """
        Get all active users with pagination.
        Delegates to GetAllUsersUseCase.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List of UserResponse objects
        """
        try:
            logger.info(f"Getting all users with skip: {skip}, limit: {limit}")
            input_data = GetAllUsersInput(skip=skip, limit=limit)
            return await self.get_all_users_use_case.execute(input_data)
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise

    async def update_user(
        self, user_id: str, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """
        Update user information.
        Delegates to UpdateUserUseCase.

        Args:
            user_id: User ID to update
            user_data: UserUpdate schema with fields to update

        Returns:
            Updated UserResponse if found, None otherwise

        Raises:
            ValueError: If new email already exists
        """
        try:
            logger.info(f"Updating user with ID: {user_id}")
            input_data = UpdateUserInput(user_id=user_id, user_data=user_data)
            return await self.update_user_use_case.execute(input_data)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete (deactivate) a user account.
        Delegates to DeleteUserUseCase.

        Args:
            user_id: User ID to delete

        Returns:
            True if user was deleted, False otherwise
        """
        try:
            logger.info(f"Deleting user with ID: {user_id}")
            return await self.delete_user_use_case.execute(user_id)
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise
