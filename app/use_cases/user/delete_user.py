"""Delete User use case."""

from app.domain.interfaces.user_repository_interface import IUserRepository
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class DeleteUserUseCase(IUseCase[str, bool]):
    """Use case for deleting (deactivating) a user account."""
    
    def __init__(self, repository: IUserRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IUserRepository
        """
        self.repository = repository
    
    async def execute(self, user_id: str) -> bool:
        """
        Delete (soft delete) a user account by deactivating it.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if user was deleted, False otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Deleting user with ID: {user_id}")
            
            deleted = await self.repository.delete(user_id)
            
            if deleted:
                logger.info(f"User deleted successfully with ID: {user_id}")
                return True
            
            logger.warning(f"User not found for deletion with ID: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user with ID {user_id}: {e}")
            raise
