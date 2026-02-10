"""Get All Expenses use case."""

from typing import List
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.models.expense_schema import ExpenseResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase
from app.domain.dtos.expense_dtos import GetAllExpensesInput

logger = get_logger(__name__)


class GetAllExpensesUseCase(IUseCase[GetAllExpensesInput, List[ExpenseResponse]]):
    """Use case for retrieving all expenses for a group."""
    
    def __init__(self, repository: IExpenseRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IExpenseRepository
        """
        self.repository = repository
    
    async def execute(
        self, 
        input_data: GetAllExpensesInput
    ) -> List[ExpenseResponse]:
        """
        Get all expenses for a group from all participants.
        
        Args:
            input_data: GetAllExpensesInput DTO containing group_id, skip, and limit
            
        Returns:
            List of ExpenseResponse objects from all group participants
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Fetching all expenses for group: {input_data.group_id} (skip={input_data.skip}, limit={input_data.limit})")
            
            expenses = await self.repository.get_all(input_data.group_id, skip=input_data.skip, limit=input_data.limit)
            
            logger.info(f"Retrieved {len(expenses)} expenses from all participants in group: {input_data.group_id}")
            return [ExpenseResponse(**expense.model_dump()) for expense in expenses]
        except Exception as e:
            logger.error(f"Error fetching expenses for group {input_data.group_id}: {e}")
            raise
