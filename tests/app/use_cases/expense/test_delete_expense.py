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
        assert hasattr(use_case, 'execute')


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
