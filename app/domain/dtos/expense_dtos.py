"""Data Transfer Objects for Expense use cases."""

from typing import NamedTuple
from app.models.expense_schema import ExpenseUpdate


class GetAllExpensesInput(NamedTuple):
    """Input data for GetAllExpensesUseCase."""
    group_id: str
    skip: int = 0
    limit: int = 100


class UpdateExpenseInput(NamedTuple):
    """Input data for UpdateExpenseUseCase."""
    expense_id: str
    expense_data: ExpenseUpdate
