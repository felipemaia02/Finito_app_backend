"""Update Expense use case."""

from typing import Optional
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.models.expense_schema import ExpenseResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase
from app.domain.dtos.expense_dtos import UpdateExpenseInput

logger = get_logger(__name__)


class UpdateExpenseUseCase(IUseCase[UpdateExpenseInput, Optional[ExpenseResponse]]):
    """Use case for updating an existing expense."""
    
    def __init__(self, repository: IExpenseRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IExpenseRepository
        """
        self.repository = repository
    
    async def execute(self, input_data: UpdateExpenseInput) -> Optional[ExpenseResponse]:
        """
        Update an existing expense.
        
        Args:
            input_data: UpdateExpenseInput with expense_id and expense_data
            
        Returns:
            ExpenseResponse with updated expense if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Updating expense with ID: {input_data.expense_id}")
            
            current_expense = await self.repository.get_by_id(input_data.expense_id)
            if not current_expense:
                logger.warning(f"Expense not found for update: {input_data.expense_id}")
                return None

            update_dict = input_data.expense_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                if value is not None:
                    setattr(current_expense, key, value)
            
            current_expense.update_timestamp()

            updated_expense = await self.repository.update(input_data.expense_id, current_expense)
            
            if updated_expense:
                logger.info(f"Expense updated successfully: {input_data.expense_id}")
                return ExpenseResponse(**updated_expense.model_dump())
            
            logger.warning(f"Failed to update expense: {input_data.expense_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating expense {input_data.expense_id}: {e}")
            raise
