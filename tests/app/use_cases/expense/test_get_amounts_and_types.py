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
        assert hasattr(use_case, 'execute')


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
