"""Create Expense use case."""

from datetime import datetime, timezone
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.entities.expense_entity import Expense
from app.models.expense_schema import ExpenseCreate, ExpenseResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class CreateExpenseUseCase(IUseCase[ExpenseCreate, ExpenseResponse]):
    """Use case for creating a new expense in a group."""
    
    def __init__(self, repository: IExpenseRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IExpenseRepository
        """
        self.repository = repository
    
    async def execute(self, expense_data: ExpenseCreate) -> ExpenseResponse:
        """
        Create a new expense in a group.
        Multiple participants can add expenses to the same group (group_id).
        
        Args:
            expense_data: ExpenseCreate schema with expense details
            
        Returns:
            ExpenseResponse with the created expense
            
        Raises:
            ValueError: If expense data is invalid
            Exception: If database operation fails
        """
        try:
            logger.info(f"Creating expense for group: {expense_data.group_id} by {expense_data.spent_by}")
            
            expense = Expense(
                group_id=expense_data.group_id,
                amount_cents=expense_data.amount_cents,
                category=expense_data.category,
                type_expense=expense_data.type_expense,
                spent_by=expense_data.spent_by,
                date=expense_data.date or datetime.now(timezone.utc),
                note=expense_data.note,
                is_deleted=False
            )

            created_expense = await self.repository.create(expense)
            
            logger.info(f"Expense created successfully with ID: {created_expense.id}")
            return ExpenseResponse(**created_expense.model_dump())
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            raise
