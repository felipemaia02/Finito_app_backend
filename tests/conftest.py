"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, date, timedelta
from bson import ObjectId

from app.domain.entities.expense_entity import Expense
from app.domain.entities.user_entity import User
from app.domain.entities.group_entity import Group
from app.domain.entities.email_verification_token_entity import EmailVerificationToken
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.models.user_schema import UserCreate, UserUpdate, UserResponse
from app.models.group_schema import GroupCreate, GroupUpdate, GroupResponse
from app.models.email_verification_schema import UserRegisterResponse
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.interfaces.group_repository_interface import IGroupRepository
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.interfaces.email_service_interface import IEmailService


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
        "name": "John Silva",
        "email": "john@example.com",
        "password": "$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",  # hashed password
        "date_birth": date(1990, 5, 15),
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
        name="Mary Silva",
        email="mary@example.com",
        password="password123!@#",
        date_birth=date(1992, 3, 20),
    )


@pytest.fixture
def sample_user_update() -> UserUpdate:
    """Provide sample user update data for testing."""
    return UserUpdate(
        name="John Silva Santos",
        email="john.silva@example.com",
    )


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Provide a mocked user repository for testing."""
    mock = AsyncMock(spec=IUserRepository)
    return mock


GROUP_ID = str(ObjectId())
USER_ID_1 = str(ObjectId())
USER_ID_2 = str(ObjectId())


@pytest.fixture
def sample_group_data() -> dict:
    """Provide sample group data for testing."""
    return {
        "id": GROUP_ID,
        "group_name": "Viagem Europa 2026",
        "creator_id": USER_ID_1,
        "user_ids": [USER_ID_1, USER_ID_2],
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_group_entity(sample_group_data) -> Group:
    """Provide sample group entity for testing."""
    return Group(**sample_group_data)


@pytest.fixture
def sample_group_create() -> GroupCreate:
    """Provide sample group creation data for testing."""
    return GroupCreate(group_name="Viagem Europa 2026")


@pytest.fixture
def sample_group_update() -> GroupUpdate:
    """Provide sample group update data for testing."""
    return GroupUpdate(group_name="Viagem Europa 2027")


@pytest.fixture
def sample_group_response(sample_group_data, sample_user_data) -> GroupResponse:
    """Provide sample group response model for testing."""
    user_resp = UserResponse(**sample_user_data)
    return GroupResponse(
        id=sample_group_data["id"],
        group_name=sample_group_data["group_name"],
        users=[user_resp],
        created_at=sample_group_data["created_at"],
        updated_at=sample_group_data["updated_at"],
    )


@pytest.fixture
def mock_group_repository() -> AsyncMock:
    """Provide a mocked group repository for testing."""
    return AsyncMock(spec=IGroupRepository)


@pytest.fixture
def mock_database(mocker):
    """Provide a mocked database for testing."""
    mock_db = MagicMock()
    mocker.patch("app.infrastructure.database.Database.get_db", return_value=mock_db)
    return mock_db


@pytest.fixture
def mock_app_dependencies(mock_user_repository, mock_expense_repository, mock_verification_repository, mock_email_service):
    """Override app dependencies with mocks for testing."""
    from app.api import app
    from app.infrastructure.dependencies.user_dependencies import UserDependencies
    from app.infrastructure.dependencies.expense_dependencies import ExpenseDependencies

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

    # Default verification repository behavior
    mock_verification_repository.get_latest_by_user_id.return_value = None
    mock_verification_repository.invalidate_all_by_user_id.return_value = None
    mock_verification_repository.create.return_value = None
    mock_email_service.send_verification_email.return_value = None

    # Store original overrides
    original_overrides = app.dependency_overrides.copy()

    # Override dependencies
    app.dependency_overrides[UserDependencies.get_repository] = (
        lambda: mock_user_repository
    )
    app.dependency_overrides[UserDependencies.get_verification_repository] = (
        lambda: mock_verification_repository
    )
    app.dependency_overrides[UserDependencies.get_email_service] = (
        lambda: mock_email_service
    )
    app.dependency_overrides[ExpenseDependencies.get_repository] = (
        lambda: mock_expense_repository
    )

    yield app

    # Restore original overrides
    app.dependency_overrides = original_overrides


@pytest.fixture
def authenticated_client(mock_app_dependencies):
    """Provide test client with authentication header."""
    from fastapi.testclient import TestClient
    from app.infrastructure.settings import get_settings

    client = TestClient(mock_app_dependencies)
    # Add default API key header
    client.headers.update({"X-API-Key": get_settings().api_key})
    return client


@pytest.fixture
def valid_oauth2_token():
    """Provide a valid OAuth2 token for testing."""
    from app.services.oauth2_service import OAuth2Service

    oauth2_service = OAuth2Service()
    token, _, _ = oauth2_service.create_token_pair(email="test@example.com")
    return token


@pytest.fixture
def authenticated_client_with_token(mock_app_dependencies, valid_oauth2_token):
    """Provide test client with both API key and OAuth2 token."""
    from fastapi.testclient import TestClient
    from app.infrastructure.settings import get_settings

    client = TestClient(mock_app_dependencies)
    # Add both API key and OAuth2 token headers
    client.headers.update(
        {
            "X-API-Key": get_settings().api_key,
            "Authorization": f"Bearer {valid_oauth2_token}",
        }
    )
    return client


# ---------------------------------------------------------------------------
# Email Verification fixtures
# ---------------------------------------------------------------------------

USER_UNVERIFIED_ID = str(ObjectId())


@pytest.fixture
def sample_verification_token_data() -> dict:
    """Provide sample email verification token data for testing."""
    import hashlib

    code = "382910"
    return {
        "id": str(ObjectId()),
        "user_id": USER_UNVERIFIED_ID,
        "code_hash": hashlib.sha256(code.encode()).hexdigest(),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15),
        "is_used": False,
        "attempts": 0,
        "resend_count": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_verification_token_entity(
    sample_verification_token_data,
) -> EmailVerificationToken:
    """Provide sample EmailVerificationToken entity for testing."""
    return EmailVerificationToken(**sample_verification_token_data)


@pytest.fixture
def sample_unverified_user_data() -> dict:
    """Provide sample unverified user data for testing."""
    return {
        "id": USER_UNVERIFIED_ID,
        "name": "Maria Unverified",
        "email": "maria@example.com",
        "password": "$2b$12$abcdefghijklmnopqrstuvwxyz1234567890",
        "date_birth": date(1995, 8, 20),
        "is_active": False,
        "is_email_verified": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def sample_unverified_user_entity(sample_unverified_user_data) -> User:
    """Provide sample unverified User entity for testing."""
    return User(**sample_unverified_user_data)


@pytest.fixture
def sample_user_register_response() -> UserRegisterResponse:
    """Provide sample UserRegisterResponse for testing."""
    return UserRegisterResponse(
        message="User registered successfully. Check your email for the verification code.",
        verification_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test",
    )


@pytest.fixture
def mock_verification_repository() -> AsyncMock:
    """Provide a mocked email verification repository for testing."""
    return AsyncMock(spec=IEmailVerificationRepository)


@pytest.fixture
def mock_email_service() -> AsyncMock:
    """Provide a mocked email service for testing."""
    return AsyncMock(spec=IEmailService)


@pytest.fixture
def valid_verification_token() -> str:
    """Provide a valid email verification JWT for testing."""
    from app.services.oauth2_service import OAuth2Service

    oauth_service = OAuth2Service()
    return oauth_service.create_verification_token(user_id=USER_UNVERIFIED_ID)
