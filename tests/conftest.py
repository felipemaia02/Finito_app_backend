"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from bson import ObjectId

from app.domain.entities.expense_entity import Expense
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


@pytest.fixture
def sample_expense_data() -> dict:
    """Provide sample expense data for testing."""
    return {
        "id": str(ObjectId()),
        "group_id": "507f1f77bcf86cd799439012",
        "amount_cents": 5000,
        "category": ExpenseCategory.ENTERTAINMENT,
        "type_expense": ExpenseType.CREDIT_CARD,
        "description": "Movie tickets",
        "spent_by": "John Doe",
        "date": datetime.now(timezone.utc),
        "note": "Weekend movie",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_deleted": False,
    }


@pytest.fixture
def sample_expense_entity(sample_expense_data) -> Expense:
    """Provide sample expense entity for testing."""
    return Expense(**sample_expense_data)


@pytest.fixture
def sample_expense_response(sample_expense_data) -> ExpenseResponse:
    """Provide sample expense response model for testing."""
    return ExpenseResponse(**sample_expense_data)


@pytest.fixture
def sample_expense_create() -> ExpenseCreate:
    """Provide sample expense creation data for testing."""
    return ExpenseCreate(
        group_id="507f1f77bcf86cd799439012",
        amount_cents=5000,
        category=ExpenseCategory.UTILITIES,
        type_expense=ExpenseType.CREDIT_CARD,
        spent_by="John Doe",
        note="Weekend expense",
    )


@pytest.fixture
def sample_expense_update() -> ExpenseUpdate:
    """Provide sample expense update data for testing."""
    return ExpenseUpdate(
        amount_cents=6000,
        description="Movie tickets - updated",
        note="Updated note",
    )


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Provide a mocked expense repository for testing."""
    mock = AsyncMock(spec=IExpenseRepository)
    return mock


@pytest.fixture
def mock_database(mocker):
    """Provide a mocked database for testing."""
    mock_db = MagicMock()
    mocker.patch("app.infrastructure.database.Database.get_db", return_value=mock_db)
    return mock_db
