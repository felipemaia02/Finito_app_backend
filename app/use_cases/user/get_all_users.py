"""Get All Users use case."""

from typing import List
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.dtos.user_dtos import GetAllUsersInput
from app.models.user_schema import UserResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class GetAllUsersUseCase(IUseCase[GetAllUsersInput, List[UserResponse]]):
    """Use case for retrieving all active users."""
    
    def __init__(self, repository: IUserRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IUserRepository
        """
        self.repository = repository
    
    async def execute(self, input_data: GetAllUsersInput) -> List[UserResponse]:
        """
        Get all active users with pagination.
        
        Args:
            input_data: Pagination parameters (skip, limit)
            
        Returns:
            List of UserResponse objects
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Retrieving users with skip: {input_data.skip}, limit: {input_data.limit}")
            
            users = await self.repository.get_all(
                skip=input_data.skip,
                limit=input_data.limit
            )
            
            logger.info(f"Retrieved {len(users)} users")
            return [UserResponse(**user.model_dump()) for user in users]
        except Exception as e:
            logger.error(f"Error retrieving all users: {e}")
            raise
