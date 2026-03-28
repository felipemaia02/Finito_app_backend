"""Tests for use_cases/expense/delete_expense.py"""

import pytest
from unittest.mock import AsyncMock
from app.use_cases.expense.delete_expense import DeleteExpenseUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


class TestDeleteExpenseUseCase:
    """Test DeleteExpenseUseCase"""

    def test_use_case_creation(self):
        """Test creating DeleteExpenseUseCase"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = DeleteExpenseUseCase(mock_repo)
        assert use_case is not None

    def test_use_case_has_execute_method(self):
        """Test use case has execute method"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = DeleteExpenseUseCase(mock_repo)
        assert hasattr(use_case, "execute")

    @pytest.mark.asyncio
    async def test_execute_success(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.delete.return_value = True
        use_case = DeleteExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute("expense-id-123")

        # Assert
        assert result is True
        mock_expense_repository.delete.assert_called_once_with("expense-id-123")

    @pytest.mark.asyncio
    async def test_execute_not_found(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.delete.return_value = False
        use_case = DeleteExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute("nonexistent-id")

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.delete.side_effect = Exception("DB error")
        use_case = DeleteExpenseUseCase(mock_expense_repository)

        # Act & Assert
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute("some-id")


class TestDeleteExpenseStructure:
    """Test DeleteExpenseUseCase structure"""

    def test_use_case_class_exists(self):
        """Test DeleteExpenseUseCase class exists"""
        assert DeleteExpenseUseCase is not None

    def test_use_case_is_instantiable(self):
        """Test DeleteExpenseUseCase can be instantiated"""
        mock_repo = AsyncMock()
        use_case = DeleteExpenseUseCase(mock_repo)
        assert isinstance(use_case, DeleteExpenseUseCase)
