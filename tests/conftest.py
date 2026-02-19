"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, date
from bson import ObjectId

from app.domain.entities.expense_entity import Expense
from app.domain.entities.user_entity import User
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.models.user_schema import UserCreate, UserUpdate, UserResponse
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.interfaces.user_repository_interface import IUserRepository


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
def mock_expense_repository() -> AsyncMock:
    """Provide a mocked expense repository for testing."""
    mock = AsyncMock(spec=IExpenseRepository)
    return mock


@pytest.fixture
def sample_user_data() -> dict:
    """Provide sample user data for testing."""
    return {
        "id": str(ObjectId()),
        "nome": "João Silva",
        "email": "joao@example.com",
        "senha": "$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",  # hashed password
        "data_nascimento": date(1990, 5, 15),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_user_entity(sample_user_data) -> User:
    """Provide sample user entity for testing."""
    return User(**sample_user_data)


@pytest.fixture
def sample_user_response(sample_user_data) -> UserResponse:
    """Provide sample user response model for testing."""
    return UserResponse(**sample_user_data)


@pytest.fixture
def sample_user_create() -> UserCreate:
    """Provide sample user creation data for testing."""
    return UserCreate(
        nome="Maria Silva",
        email="maria@example.com",
        senha="password123!@#",
        data_nascimento=date(1992, 3, 20),
    )


@pytest.fixture
def sample_user_update() -> UserUpdate:
    """Provide sample user update data for testing."""
    return UserUpdate(
        nome="João Silva Santos",
        email="joao.silva@example.com",
    )


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Provide a mocked user repository for testing."""
    mock = AsyncMock(spec=IUserRepository)
    return mock


@pytest.fixture
def mock_database(mocker):
    """Provide a mocked database for testing."""
    mock_db = MagicMock()
    mocker.patch("app.infrastructure.database.Database.get_db", return_value=mock_db)
    return mock_db


@pytest.fixture
def mock_app_dependencies(mock_user_repository, mock_expense_repository):
    """Override app dependencies with mocks for testing."""
    from app.api import app
    from app.infrastructure.user_dependencies import UserDependencies
    from app.infrastructure.dependencies import ExpenseDependencies
    
    # Configure default mock behavior
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.email_exists.return_value = False
    mock_user_repository.get_by_id.return_value = None
    mock_user_repository.get_all.return_value = []
    mock_user_repository.delete.return_value = False
    mock_user_repository.update.return_value = None
    
    mock_expense_repository.get_by_id.return_value = None
    mock_expense_repository.get_all.return_value = []
    mock_expense_repository.delete.return_value = False
    
    # Store original overrides
    original_overrides = app.dependency_overrides.copy()
    
    # Override dependencies
    app.dependency_overrides[UserDependencies.get_repository] = lambda: mock_user_repository
    app.dependency_overrides[ExpenseDependencies.get_repository] = lambda: mock_expense_repository
    
    yield app
    
    # Restore original overrides
    app.dependency_overrides = original_overrides

