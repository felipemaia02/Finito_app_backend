"""Tests for use_cases/expense/get_expense_by_id.py"""

import pytest
from unittest.mock import AsyncMock
from app.use_cases.expense.get_expense_by_id import GetExpenseByIdUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


class TestGetExpenseByIdUseCase:
    """Test GetExpenseByIdUseCase"""

    def test_use_case_creation(self):
        """Test creating GetExpenseByIdUseCase"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = GetExpenseByIdUseCase(mock_repo)
        assert use_case is not None

    def test_use_case_has_execute_method(self):
        """Test use case has execute method"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = GetExpenseByIdUseCase(mock_repo)
        assert hasattr(use_case, "execute")

    @pytest.mark.asyncio
    async def test_execute_found(self, mock_expense_repository, sample_expense_entity):
        # Arrange
        mock_expense_repository.get_by_id.return_value = sample_expense_entity
        use_case = GetExpenseByIdUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute(sample_expense_entity.id)

        # Assert
        assert result is not None
        assert result.id == sample_expense_entity.id
        mock_expense_repository.get_by_id.assert_called_once_with(
            sample_expense_entity.id
        )

    @pytest.mark.asyncio
    async def test_execute_not_found(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.get_by_id.return_value = None
        use_case = GetExpenseByIdUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute("nonexistent-id")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.get_by_id.side_effect = Exception("DB error")
        use_case = GetExpenseByIdUseCase(mock_expense_repository)

        # Act & Assert
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute("some-id")


class TestGetExpenseByIdStructure:
    """Test GetExpenseByIdUseCase structure"""

    def test_use_case_class_exists(self):
        """Test GetExpenseByIdUseCase class exists"""
        assert GetExpenseByIdUseCase is not None

    def test_use_case_is_instantiable(self):
        """Test GetExpenseByIdUseCase can be instantiated"""
        mock_repo = AsyncMock()
        use_case = GetExpenseByIdUseCase(mock_repo)
        assert isinstance(use_case, GetExpenseByIdUseCase)
