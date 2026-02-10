"""Get Expense By ID use case."""

from typing import Optional
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.models.expense_schema import ExpenseResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class GetExpenseByIdUseCase(IUseCase[str, Optional[ExpenseResponse]]):
    """Use case for retrieving a specific expense by ID."""
    
    def __init__(self, repository: IExpenseRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IExpenseRepository
        """
        self.repository = repository
    
    async def execute(self, expense_id: str) -> Optional[ExpenseResponse]:
        """
        Get a specific expense by ID.
        
        Args:
            expense_id: ID of the expense to retrieve
            
        Returns:
            ExpenseResponse if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Fetching expense with ID: {expense_id}")
            
            expense = await self.repository.get_by_id(expense_id)
            
            if expense:
                logger.info(f"Expense found: {expense_id}")
                return ExpenseResponse(**expense.model_dump())
            
            logger.warning(f"Expense not found: {expense_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching expense {expense_id}: {e}")
            raise
