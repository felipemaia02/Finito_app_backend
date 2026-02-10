"""Tests for use_cases/expense/create_expense.py"""

import pytest
from unittest.mock import AsyncMock
from app.use_cases.expense.create_expense import CreateExpenseUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


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
        assert hasattr(use_case, 'execute')
        assert callable(use_case.execute)


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
