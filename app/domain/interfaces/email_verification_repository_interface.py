"""
Interface for email verification token repository.
"""

from typing import Optional
from abc import abstractmethod
from app.domain.interfaces.repository import BaseRepository
from app.domain.entities.email_verification_token_entity import EmailVerificationToken


class IEmailVerificationRepository(BaseRepository[EmailVerificationToken]):
    """
    Interface for email verification token repository operations.
    Extends the base repository with verification-specific queries.
    """

    @abstractmethod
    async def get_valid_token_by_user_id(
        self, user_id: str
    ) -> Optional[EmailVerificationToken]:
        """
        Get the active (non-used, non-expired) token for a user.

        Args:
            user_id: The user's ID

        Returns:
            EmailVerificationToken if a valid one exists, None otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    async def get_latest_by_user_id(
        self, user_id: str
    ) -> Optional[EmailVerificationToken]:
        """
        Get the most recently created token for a user (regardless of status).
        Used to retrieve resend_count when issuing a new token.

        Args:
            user_id: The user's ID

        Returns:
            Most recent EmailVerificationToken or None
        """
        pass  # pragma: no cover

    @abstractmethod
    async def mark_as_used(self, token_id: str) -> None:
        """
        Mark a token as consumed so it cannot be reused.

        Args:
            token_id: Token ID to mark as used
        """
        pass  # pragma: no cover

    @abstractmethod
    async def increment_attempts(self, token_id: str) -> None:
        """
        Increment the failed attempt counter for a token.

        Args:
            token_id: Token ID to increment attempts for
        """
        pass  # pragma: no cover

    @abstractmethod
    async def invalidate_all_by_user_id(self, user_id: str) -> None:
        """
        Mark all existing tokens for a user as used (e.g., before issuing a new one).

        Args:
            user_id: The user's ID
        """
        pass  # pragma: no cover
