"""Interface for OAuth2 authentication service."""

from abc import ABC, abstractmethod
from typing import Optional
from app.models.auth_schema import TokenData


class IOAuth2Service(ABC):
    """Interface for OAuth2/JWT authentication service."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        pass  # pragma: no cover

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        pass  # pragma: no cover

    @abstractmethod
    def create_access_token(self, data: dict, expires_delta=None) -> str:
        """Create a JWT access token."""
        pass  # pragma: no cover

    @abstractmethod
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        pass  # pragma: no cover
