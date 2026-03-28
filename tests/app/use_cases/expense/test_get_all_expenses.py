"""Tests for use_cases/expense/get_all_expenses.py"""

import pytest
from unittest.mock import AsyncMock
from app.use_cases.expense.get_all_expenses import GetAllExpensesUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.dtos.expense_dtos import GetAllExpensesInput


class TestGetAllExpensesUseCase:
    """Test GetAllExpensesUseCase"""

    def test_use_case_creation(self):
        """Test creating GetAllExpensesUseCase"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = GetAllExpensesUseCase(mock_repo)
        assert use_case is not None

    def test_use_case_has_execute_method(self):
        """Test use case has execute method"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = GetAllExpensesUseCase(mock_repo)
        assert hasattr(use_case, "execute")

    @pytest.mark.asyncio
    async def test_execute_returns_expenses(
        self, mock_expense_repository, sample_expense_entity
    ):
        # Arrange
        mock_expense_repository.get_all.return_value = [sample_expense_entity]
        use_case = GetAllExpensesUseCase(mock_expense_repository)
        input_data = GetAllExpensesInput(
            group_id="507f1f77bcf86cd799439012", skip=0, limit=100
        )

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert len(result) == 1
        assert result[0].group_id == sample_expense_entity.group_id
        mock_expense_repository.get_all.assert_called_once_with(
            "507f1f77bcf86cd799439012", skip=0, limit=100
        )

    @pytest.mark.asyncio
    async def test_execute_empty_list(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.get_all.return_value = []
        use_case = GetAllExpensesUseCase(mock_expense_repository)
        input_data = GetAllExpensesInput(group_id="group-123")

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_execute_passes_pagination(
        self, mock_expense_repository, sample_expense_entity
    ):
        # Arrange
        mock_expense_repository.get_all.return_value = [sample_expense_entity]
        use_case = GetAllExpensesUseCase(mock_expense_repository)
        input_data = GetAllExpensesInput(group_id="grp", skip=10, limit=5)

        # Act
        await use_case.execute(input_data)

        # Assert
        mock_expense_repository.get_all.assert_called_once_with("grp", skip=10, limit=5)

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self, mock_expense_repository):
        # Arrange
        mock_expense_repository.get_all.side_effect = Exception("DB error")
        use_case = GetAllExpensesUseCase(mock_expense_repository)
        input_data = GetAllExpensesInput(group_id="grp")

        # Act & Assert
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute(input_data)


class TestGetAllExpensesStructure:
    """Test GetAllExpensesUseCase structure"""

    def test_use_case_class_exists(self):
        """Test GetAllExpensesUseCase class exists"""
        assert GetAllExpensesUseCase is not None

    def test_use_case_is_instantiable(self):
        """Test GetAllExpensesUseCase can be instantiated"""
        mock_repo = AsyncMock()
        use_case = GetAllExpensesUseCase(mock_repo)
        assert isinstance(use_case, GetAllExpensesUseCase)
