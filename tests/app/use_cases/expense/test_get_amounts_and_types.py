"""Tests for use_cases/expense/get_amounts_and_types.py"""

import pytest
from unittest.mock import AsyncMock
from app.use_cases.expense.get_amounts_and_types import GetAmountsAndTypesUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


class TestGetAmountsAndTypesUseCase:
    """Test GetAmountsAndTypesUseCase"""

    def test_use_case_creation(self):
        """Test creating GetAmountsAndTypesUseCase"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = GetAmountsAndTypesUseCase(mock_repo)
        assert use_case is not None

    def test_use_case_has_execute_method(self):
        """Test use case has execute method"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = GetAmountsAndTypesUseCase(mock_repo)
        assert hasattr(use_case, "execute")

    @pytest.mark.asyncio
    async def test_execute_returns_data(self, mock_expense_repository):
        # Arrange
        expected = [
            {"amount_cents": 5000, "type_expense": "credit_card"},
            {"amount_cents": 2000, "type_expense": "cash"},
        ]
        mock_expense_repository.get_amounts_and_types.return_value = expected
        use_case = GetAmountsAndTypesUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute("group-123")

        # Assert
        assert result == expected
        mock_expense_repository.get_amounts_and_types.assert_called_once_with(
            "group-123"
        )

    @pytest.mark.asyncio
    async def test_execute_empty(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.get_amounts_and_types.return_value = []
        use_case = GetAmountsAndTypesUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute("group-empty")

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.get_amounts_and_types.side_effect = Exception(
            "DB error"
        )
        use_case = GetAmountsAndTypesUseCase(mock_expense_repository)

        # Act & Assert
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute("group-fail")


class TestGetAmountsAndTypesStructure:
    """Test GetAmountsAndTypesUseCase structure"""

    def test_use_case_class_exists(self):
        """Test GetAmountsAndTypesUseCase class exists"""
        assert GetAmountsAndTypesUseCase is not None

    def test_use_case_is_instantiable(self):
        """Test GetAmountsAndTypesUseCase can be instantiated"""
        mock_repo = AsyncMock()
        use_case = GetAmountsAndTypesUseCase(mock_repo)
        assert isinstance(use_case, GetAmountsAndTypesUseCase)
