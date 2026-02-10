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
        assert hasattr(use_case, 'execute')


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
