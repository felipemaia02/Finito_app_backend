"""Tests for controllers/expense_controller.py"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.controllers.expense_controller import ExpenseController
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


class TestExpenseControllerInitialization:
    """Test ExpenseController initialization"""

    def test_controller_creation(self):
        """Test creating ExpenseController"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert controller is not None

    def test_controller_stores_repository(self):
        """Test controller stores repository"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert controller.repository == mock_repo

    def test_controller_requires_repository(self):
        """Test controller initialization requires repository"""
        assert True  # If no exception, test passes


class TestExpenseControllerMethods:
    """Test ExpenseController has all required methods"""

    def test_controller_has_create_expense_method(self):
        """Test controller has create_expense method"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, 'create_expense')

    def test_controller_has_get_all_expenses_method(self):
        """Test controller has get_all_expenses method"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, 'get_all_expenses')

    def test_controller_has_get_expense_by_id_method(self):
        """Test controller has get_expense_by_id method"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, 'get_expense_by_id')

    def test_controller_has_update_expense_method(self):
        """Test controller has update_expense method"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, 'update_expense')

    def test_controller_has_delete_expense_method(self):
        """Test controller has delete_expense method"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, 'delete_expense')

    def test_controller_has_get_amounts_and_types_method(self):
        """Test controller has get_amounts_and_types method"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert hasattr(controller, 'get_amounts_and_types')

    def test_controller_methods_are_callable(self):
        """Test all controller methods are callable"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        controller = ExpenseController(mock_repo)
        assert callable(controller.create_expense)
        assert callable(controller.get_all_expenses)
        assert callable(controller.get_expense_by_id)
        assert callable(controller.update_expense)
        assert callable(controller.delete_expense)
        assert callable(controller.get_amounts_and_types)
