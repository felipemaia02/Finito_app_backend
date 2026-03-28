"""Dependency injection container for user operations."""

from fastapi import Depends

from app.controllers.user_controller import UserController
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.infrastructure.repositories.user_repository import MongoUserRepository


class UserDependencies:
    """Container for managing user-related dependencies."""

    @staticmethod
    def get_repository() -> IUserRepository:
        """
        Provides the user repository instance.

        Returns:
            IUserRepository: MongoDB implementation of user repository
        """
        return MongoUserRepository()

    @staticmethod
    def get_controller(
        repository: IUserRepository = Depends(get_repository.__func__),
    ) -> UserController:
        """
        Provides the user controller instance with injected repository.

        Args:
            repository: Injected user repository

        Returns:
            UserController: Controller instance with repository
        """
        return UserController(repository)
