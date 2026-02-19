"""Authentication service interface."""

from abc import ABC, abstractmethod


class IAuthService(ABC):
    """Interface for authentication services."""

    @abstractmethod
    async def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
