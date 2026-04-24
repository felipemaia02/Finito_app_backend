"""
Interface for the email sending service.
"""

from abc import ABC, abstractmethod


class IEmailService(ABC):
    """Contract for email sending implementations."""

    @abstractmethod
    async def send_verification_email(self, to_email: str, code: str) -> None:
        """
        Send a verification code email to the user.

        Args:
            to_email: Recipient email address
            code: Plain-text 6-digit verification code

        Raises:
            Exception: If the email fails to send
        """
        pass  # pragma: no cover
