"""
User repository interface for user-specific operations.
"""

from typing import List, Optional
from abc import abstractmethod
from app.domain.interfaces.repository import BaseRepository
from app.domain.entities.user_entity import User


class IUserRepository(BaseRepository[User]):
    """
    Interface for user repository operations.
    Extends the base repository with user-specific queries.
    """

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all active users with pagination.

        Args:
            skip: Number of users to skip for pagination
            limit: Maximum number of users to return

        Returns:
            List of active users
        """
        pass  # pragma: no cover

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.

        Args:
            email: User's email address

        Returns:
            User entity if found, None otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists in the system.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    async def get_by_id_unverified(self, id: str) -> Optional[User]:
        """
        Get a user by ID regardless of is_active status.
        Used exclusively in the email verification flow.

        Args:
            id: User ID

        Returns:
            User entity if found (active or not), None otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    async def get_by_email_unverified(self, email: str) -> Optional[User]:
        """
        Get a user by email regardless of is_active/is_email_verified status.
        Used exclusively in the email verification flow.

        Args:
            email: User's email address

        Returns:
            User entity if found (active or not), None otherwise
        """
        pass  # pragma: no cover
