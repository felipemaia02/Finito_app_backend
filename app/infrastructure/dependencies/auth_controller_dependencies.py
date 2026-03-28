"""Authentication dependencies for FastAPI."""

from app.infrastructure.repositories.user_repository import MongoUserRepository
from app.controllers.auth_controller import AuthController


class AuthDependencies:
    """Container for managing authentication-related dependencies."""

    @staticmethod
    def get_controller() -> AuthController:
        """
        Get the authentication controller instance.

        Returns:
            AuthController instance with repository dependency
        """
        repository = MongoUserRepository()
        return AuthController(repository)
