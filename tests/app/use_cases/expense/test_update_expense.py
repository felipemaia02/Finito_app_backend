"""Tests for use_cases/expense/update_expense.py"""

import pytest
from unittest.mock import AsyncMock
from app.use_cases.expense.update_expense import UpdateExpenseUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.domain.dtos.expense_dtos import UpdateExpenseInput
from app.models.expense_schema import ExpenseUpdate


class TestUpdateExpenseUseCase:
    """Test UpdateExpenseUseCase"""

    def test_use_case_creation(self):
        """Test creating UpdateExpenseUseCase"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = UpdateExpenseUseCase(mock_repo)
        assert use_case is not None

    def test_use_case_has_execute_method(self):
        """Test use case has execute method"""
        mock_repo = AsyncMock(spec=IExpenseRepository)
        use_case = UpdateExpenseUseCase(mock_repo)
        assert hasattr(use_case, "execute")

    @pytest.mark.asyncio
    async def test_execute_success(
        self, mock_expense_repository, sample_expense_entity
    ):
        # Arrange
        update_data = ExpenseUpdate(amount_cents=9999)
        input_data = UpdateExpenseInput(
            expense_id=sample_expense_entity.id, expense_data=update_data
        )
        updated_entity = sample_expense_entity
        updated_entity.amount_cents = 9999
        mock_expense_repository.get_by_id.return_value = sample_expense_entity
        mock_expense_repository.update.return_value = updated_entity
        use_case = UpdateExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is not None
        assert result.amount_cents == 9999
        mock_expense_repository.get_by_id.assert_called_once_with(
            sample_expense_entity.id
        )
        mock_expense_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_not_found_returns_none(self, mock_expense_repository):
        # Arrange
        update_data = ExpenseUpdate(amount_cents=100)
        input_data = UpdateExpenseInput(
            expense_id="nonexistent", expense_data=update_data
        )
        mock_expense_repository.get_by_id.return_value = None
        use_case = UpdateExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is None
        mock_expense_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_update_returns_none(
        self, mock_expense_repository, sample_expense_entity
    ):
        # Arrange — repo.update returns None (concurrent delete scenario)
        update_data = ExpenseUpdate(note="new note")
        input_data = UpdateExpenseInput(
            expense_id=sample_expense_entity.id, expense_data=update_data
        )
        mock_expense_repository.get_by_id.return_value = sample_expense_entity
        mock_expense_repository.update.return_value = None
        use_case = UpdateExpenseUseCase(mock_expense_repository)

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(
        self, mock_expense_repository, sample_expense_entity
    ):
        # Arrange
        update_data = ExpenseUpdate(amount_cents=500)
        input_data = UpdateExpenseInput(
            expense_id=sample_expense_entity.id, expense_data=update_data
        )
        mock_expense_repository.get_by_id.side_effect = Exception("DB error")
        use_case = UpdateExpenseUseCase(mock_expense_repository)

        # Act & Assert
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute(input_data)


class TestUpdateExpenseStructure:
    """Test UpdateExpenseUseCase structure"""

    def test_use_case_class_exists(self):
        """Test UpdateExpenseUseCase class exists"""
        assert UpdateExpenseUseCase is not None

    def test_use_case_is_instantiable(self):
        """Test UpdateExpenseUseCase can be instantiated"""
        mock_repo = AsyncMock()
        use_case = UpdateExpenseUseCase(mock_repo)
        assert isinstance(use_case, UpdateExpenseUseCase)
