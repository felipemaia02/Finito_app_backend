"""
Expense controller for handling HTTP coordination and delegating to use cases.
"""

from typing import List, Dict, Optional
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.interfaces.user_repository_interface import IUserRepository
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

    def __init__(
        self,
        repository: IExpenseRepository,
        group_repository: IGroupRepository,
        user_repository: IUserRepository,
    ):
        logger.info("Initializing ExpenseController")
        self.repository = repository
        self.group_repository = group_repository
        self.user_repository = user_repository
        self.create_expense_use_case = CreateExpenseUseCase(repository)
        self.get_all_expenses_use_case = GetAllExpensesUseCase(repository)
        self.get_expense_by_id_use_case = GetExpenseByIdUseCase(repository)
        self.update_expense_use_case = UpdateExpenseUseCase(repository)
        self.delete_expense_use_case = DeleteExpenseUseCase(repository)
        self.get_amounts_and_types_use_case = GetAmountsAndTypesUseCase(repository)
        logger.info("ExpenseController initialized successfully")

    async def _require_group_membership(self, group_id: str, user_email: str) -> None:
        """Raise PermissionError if the user is not a member of the group."""
        user = await self.user_repository.get_by_email(user_email)
        if user is None:
            raise PermissionError("You are not a member of this group")
        group = await self.group_repository.get_by_id(group_id)
        if group is None or user.id not in group.user_ids:
            raise PermissionError("You are not a member of this group")

    async def create_expense(self, expense_data: ExpenseCreate, user_email: str) -> ExpenseResponse:
        logger.info(f"Controller: Creating expense for group {expense_data.group_id}")
        await self._require_group_membership(expense_data.group_id, user_email)
        result = await self.create_expense_use_case.execute(expense_data)
        logger.info(f"Controller: Expense created with ID {result.id}")
        return result

    async def get_all_expenses(
        self, group_id: str, user_email: str, skip: int = 0, limit: int = 100
    ) -> List[ExpenseResponse]:
        logger.info(
            f"Controller: Fetching all expenses for group {group_id} (skip={skip}, limit={limit})"
        )
        await self._require_group_membership(group_id, user_email)
        input_data = GetAllExpensesInput(group_id=group_id, skip=skip, limit=limit)
        result = await self.get_all_expenses_use_case.execute(input_data)
        logger.info(
            f"Controller: Retrieved {len(result)} expenses for group {group_id}"
        )
        return result

    async def get_expense_by_id(self, expense_id: str, user_email: str) -> Optional[ExpenseResponse]:
        logger.info(f"Controller: Fetching expense with ID {expense_id}")
        expense = await self.get_expense_by_id_use_case.execute(expense_id)
        if expense is None:
            logger.warning(f"Controller: Expense not found with ID {expense_id}")
            return None
        await self._require_group_membership(expense.group_id, user_email)
        logger.info(f"Controller: Expense found with ID {expense_id}")
        return expense

    async def update_expense(
        self, expense_id: str, expense_data: ExpenseUpdate, user_email: str
    ) -> Optional[ExpenseResponse]:
        logger.info(f"Controller: Updating expense with ID {expense_id}")
        existing = await self.get_expense_by_id_use_case.execute(expense_id)
        if existing is None:
            logger.warning(f"Controller: Expense not found for update with ID {expense_id}")
            return None
        await self._require_group_membership(existing.group_id, user_email)
        input_data = UpdateExpenseInput(expense_id=expense_id, expense_data=expense_data)
        result = await self.update_expense_use_case.execute(input_data)
        if result:
            logger.info(f"Controller: Expense updated successfully with ID {expense_id}")
        return result

    async def delete_expense(self, expense_id: str, user_email: str) -> bool:
        logger.info(f"Controller: Deleting expense with ID {expense_id}")
        existing = await self.get_expense_by_id_use_case.execute(expense_id)
        if existing is None:
            logger.warning(f"Controller: Expense not found for deletion with ID {expense_id}")
            return False
        await self._require_group_membership(existing.group_id, user_email)
        result = await self.delete_expense_use_case.execute(expense_id)
        if result:
            logger.info(f"Controller: Expense deleted successfully with ID {expense_id}")
        return result

    async def get_amounts_and_types(self, group_id: str, user_email: str) -> List[Dict[str, any]]:
        logger.info(f"Controller: Fetching amounts and types for group {group_id}")
        await self._require_group_membership(group_id, user_email)
        result = await self.get_amounts_and_types_use_case.execute(group_id)
        logger.info(
            f"Controller: Retrieved amounts and types for {len(result)} expenses in group {group_id}"
        )
        return result




