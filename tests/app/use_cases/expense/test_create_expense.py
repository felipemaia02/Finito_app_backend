"""Tests for use_cases/expense/create_expense.py"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from app.use_cases.expense.create_expense import CreateExpenseUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType
from app.models.expense_schema import ExpenseCreate


class TestCreateExpenseUseCase:
    """Test CreateExpenseUseCase"""

    def test_use_case_creation(self):
        """Test creating CreateExpenseUseCase"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = CreateExpenseUseCase(mock_repo)
        assert use_case is not None

    def test_use_case_stores_repository(self):
        """Test use case stores repository"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = CreateExpenseUseCase(mock_repo)
        assert use_case.repository == mock_repo

    def test_use_case_has_execute_method(self):
        """Test use case has execute method"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = CreateExpenseUseCase(mock_repo)
        assert hasattr(use_case, "execute")
        assert callable(use_case.execute)

    @pytest.mark.asyncio
    async def test_execute_success(
        self, mock_expense_repository, sample_expense_entity, sample_expense_create
    ):
        # Arrange
        mock_expense_repository.create.return_value = sample_expense_entity
        use_case = CreateExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute(sample_expense_create)

        # Assert
        assert result is not None
        assert result.group_id == sample_expense_entity.group_id
        assert result.amount_cents == sample_expense_entity.amount_cents
        mock_expense_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_explicit_date(
        self, mock_expense_repository, sample_expense_entity
    ):
        # Arrange
        expense_data = ExpenseCreate(
            group_id="507f1f77bcf86cd799439012",
            amount_cents=1000,
            category=ExpenseCategory.GROCERIES,
            type_expense=ExpenseType.CASH,
            spent_by="Alice",
            date=datetime.now(timezone.utc),
        )
        mock_expense_repository.create.return_value = sample_expense_entity
        use_case = CreateExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute(expense_data)

        # Assert
        assert result is not None
        mock_expense_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_without_date_defaults_to_now(
        self, mock_expense_repository, sample_expense_entity
    ):
        # Arrange
        expense_data = ExpenseCreate(
            group_id="group-999",
            amount_cents=2000,
            category=ExpenseCategory.ENTERTAINMENT,
            type_expense=ExpenseType.CREDIT_CARD,
            spent_by="Bob",
        )
        mock_expense_repository.create.return_value = sample_expense_entity
        use_case = CreateExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute(expense_data)

        # Assert
        assert result is not None
        call_args = mock_expense_repository.create.call_args[0][0]
        assert call_args.date is not None

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(
        self, mock_expense_repository, sample_expense_create
    ):
        # Arrange
        mock_expense_repository.create.side_effect = Exception("DB error")
        use_case = CreateExpenseUseCase(mock_expense_repository)

        # Act & Assert
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute(sample_expense_create)


class TestCreateExpenseUseCaseStructure:
    """Test CreateExpenseUseCase structure"""

    def test_use_case_class_exists(self):
        """Test CreateExpenseUseCase class exists"""
        assert CreateExpenseUseCase is not None

    def test_use_case_is_instantiable(self):
        """Test CreateExpenseUseCase can be instantiated"""
        mock_repo = AsyncMock()
        use_case = CreateExpenseUseCase(mock_repo)
        assert isinstance(use_case, CreateExpenseUseCase)
