"""Delete Expense use case."""

from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class DeleteExpenseUseCase(IUseCase[str, bool]):
    """Use case for soft deleting an expense."""
    
    def __init__(self, repository: IExpenseRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IExpenseRepository
        """
        self.repository = repository
    
    async def execute(self, expense_id: str) -> bool:
        """
        Soft delete an expense (mark as deleted).
        
        Args:
            expense_id: ID of the expense to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Deleting expense with ID: {expense_id}")
            
            result = await self.repository.delete(expense_id)
            
            if result:
                logger.info(f"Expense deleted successfully: {expense_id}")
            else:
                logger.warning(f"Expense not found for deletion: {expense_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            raise
