"""
Expense controller for handling HTTP coordination and delegating to use cases.
"""

from typing import List, Dict, Optional
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.use_cases.expense.create_expense import CreateExpenseUseCase
from app.use_cases.expense.get_all_expenses import GetAllExpensesUseCase
from app.use_cases.expense.get_expense_by_id import GetExpenseByIdUseCase
from app.use_cases.expense.update_expense import UpdateExpenseUseCase
from app.use_cases.expense.delete_expense import DeleteExpenseUseCase
from app.use_cases.expense.get_amounts_and_types import GetAmountsAndTypesUseCase
from app.infrastructure.logger import get_logger
from app.domain.dtos.expense_dtos import GetAllExpensesInput, UpdateExpenseInput

logger = get_logger(__name__)


class ExpenseController:
    """
    Controller for expense operations.
    Coordinates between API routes and the use case layer.
    Acts as a thin HTTP coordination layer.
    """
    
    def __init__(self, repository: IExpenseRepository):
        """
        Initialize the controller with a repository dependency.
        Creates use case instances for dependency injection.
        
        Args:
            repository: Implementation of IExpenseRepository
        """
        logger.info("Initializing ExpenseController")
        self.repository = repository
        self.create_expense_use_case = CreateExpenseUseCase(repository)
        self.get_all_expenses_use_case = GetAllExpensesUseCase(repository)
        self.get_expense_by_id_use_case = GetExpenseByIdUseCase(repository)
        self.update_expense_use_case = UpdateExpenseUseCase(repository)
        self.delete_expense_use_case = DeleteExpenseUseCase(repository)
        self.get_amounts_and_types_use_case = GetAmountsAndTypesUseCase(repository)
        logger.info("ExpenseController initialized successfully")
    
    async def create_expense(self, expense_data: ExpenseCreate) -> ExpenseResponse:
        """
        Create a new expense in a group.
        Delegates to CreateExpenseUseCase.
        
        Args:
            expense_data: ExpenseCreate schema with expense details
            
        Returns:
            ExpenseResponse with the created expense
            
        Raises:
            ValueError: If expense data is invalid
            Exception: If database operation fails
        """
        logger.info(f"Controller: Creating expense for group {expense_data.group_id}")
        result = await self.create_expense_use_case.execute(expense_data)
        logger.info(f"Controller: Expense created with ID {result.id}")
        return result
    
    async def get_all_expenses(
        self, 
        group_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ExpenseResponse]:
        """
        Get all expenses for a group from all participants.
        Delegates to GetAllExpensesUseCase.
        
        Args:
            group_id: ID of the expense group
            skip: Number of expenses to skip (pagination)
            limit: Maximum number of expenses to return
            
        Returns:
            List of ExpenseResponse objects from all group participants
            
        Raises:
            Exception: If database operation fails
        """
        logger.info(f"Controller: Fetching all expenses for group {group_id} (skip={skip}, limit={limit})")
        input_data = GetAllExpensesInput(group_id=group_id, skip=skip, limit=limit)
        result = await self.get_all_expenses_use_case.execute(input_data)
        logger.info(f"Controller: Retrieved {len(result)} expenses for group {group_id}")
        return result
    
    async def get_expense_by_id(self, expense_id: str) -> Optional[ExpenseResponse]:
        """
        Get a specific expense by ID.
        Delegates to GetExpenseByIdUseCase.
        
        Args:
            expense_id: ID of the expense to retrieve
            
        Returns:
            ExpenseResponse if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        logger.info(f"Controller: Fetching expense with ID {expense_id}")
        result = await self.get_expense_by_id_use_case.execute(expense_id)
        if result:
            logger.info(f"Controller: Expense found with ID {expense_id}")
        else:
            logger.warning(f"Controller: Expense not found with ID {expense_id}")
        return result
    
    async def update_expense(self, expense_id: str, expense_data: ExpenseUpdate) -> Optional[ExpenseResponse]:
        """
        Update an existing expense.
        Delegates to UpdateExpenseUseCase.
        
        Args:
            expense_id: ID of the expense to update
            expense_data: ExpenseUpdate schema with updated fields
            
        Returns:
            ExpenseResponse with updated expense if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        logger.info(f"Controller: Updating expense with ID {expense_id}")
        input_data = UpdateExpenseInput(expense_id=expense_id, expense_data=expense_data)
        result = await self.update_expense_use_case.execute(input_data)
        if result:
            logger.info(f"Controller: Expense updated successfully with ID {expense_id}")
        else:
            logger.warning(f"Controller: Expense not found for update with ID {expense_id}")
        return result
    
    async def delete_expense(self, expense_id: str) -> bool:
        """
        Soft delete an expense (mark as deleted).
        Delegates to DeleteExpenseUseCase.
        
        Args:
            expense_id: ID of the expense to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        logger.info(f"Controller: Deleting expense with ID {expense_id}")
        result = await self.delete_expense_use_case.execute(expense_id)
        if result:
            logger.info(f"Controller: Expense deleted successfully with ID {expense_id}")
        else:
            logger.warning(f"Controller: Expense not found for deletion with ID {expense_id}")
        return result
    
    async def get_amounts_and_types(self, group_id: str) -> List[Dict[str, any]]:
        """
        Get optimized data with only amount_cents and type_expense for group analytics.
        Delegates to GetAmountsAndTypesUseCase.
        
        Args:
            group_id: ID of the expense group
            
        Returns:
            List of dictionaries with amount_cents and type_expense from all participants
            
        Raises:
            Exception: If database operation fails
        """
        logger.info(f"Controller: Fetching amounts and types for group {group_id}")
        result = await self.get_amounts_and_types_use_case.execute(group_id)
        logger.info(f"Controller: Retrieved amounts and types for {len(result)} expenses in group {group_id}")
        return result

