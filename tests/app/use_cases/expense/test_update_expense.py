"""Tests for use_cases/expense/update_expense.py"""

import pytest
from unittest.mock import AsyncMock
from app.use_cases.expense.update_expense import UpdateExpenseUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


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
        assert hasattr(use_case, 'execute')


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
