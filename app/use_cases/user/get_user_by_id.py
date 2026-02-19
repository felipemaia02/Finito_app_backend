"""Get User by ID use case."""

from typing import Optional
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.models.user_schema import UserResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class GetUserByIdUseCase(IUseCase[str, Optional[UserResponse]]):
    """Use case for retrieving a user by their ID."""
    
    def __init__(self, repository: IUserRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IUserRepository
        """
        self.repository = repository
    
    async def execute(self, user_id: str) -> Optional[UserResponse]:
        """
        Get a user by their ID.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            UserResponse if user found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Retrieving user with ID: {user_id}")
            
            user = await self.repository.get_by_id(user_id)
            
            if user:
                logger.info(f"User found with ID: {user_id}")
                return UserResponse(**user.model_dump())
            
            logger.warning(f"User not found with ID: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user with ID {user_id}: {e}")
            raise
