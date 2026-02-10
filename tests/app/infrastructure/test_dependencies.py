"""Tests for infrastructure/dependencies.py"""

import pytest
from unittest.mock import MagicMock, patch
from app.infrastructure.dependencies import ExpenseDependencies
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.controllers.expense_controller import ExpenseController


class TestExpenseDependenciesGetRepository:
    """Test ExpenseDependencies.get_repository"""

    def test_get_repository_callable(self):
        """Test get_repository is callable"""
        assert callable(ExpenseDependencies.get_repository)

    def test_get_repository_returns_repository(self):
        """Test get_repository returns a repository"""
        with patch('app.infrastructure.dependencies.MongoExpenseRepository') as mock_mongo:
            mock_repo = MagicMock()
            mock_mongo.return_value = mock_repo
            
            result = ExpenseDependencies.get_repository()
            assert result is not None

    def test_get_repository_method_exists(self):
        """Test get_repository method exists on class"""
        assert hasattr(ExpenseDependencies, 'get_repository')


class TestExpenseDependenciesGetController:
    """Test ExpenseDependencies.get_controller"""

    def test_get_controller_callable(self):
        """Test get_controller is callable"""
        assert callable(ExpenseDependencies.get_controller)

    def test_get_controller_requires_repository_parameter(self):
        """Test get_controller accepts repository parameter"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        
        controller = ExpenseDependencies.get_controller(repository=mock_repo)
        assert controller is not None

    def test_get_controller_returns_controller_instance(self):
        """Test get_controller returns controller"""
        mock_repo = MagicMock(spec=IExpenseRepository)
        
        controller = ExpenseDependencies.get_controller(repository=mock_repo)
        assert isinstance(controller, ExpenseController)

    def test_get_controller_method_exists(self):
        """Test get_controller method exists on class"""
        assert hasattr(ExpenseDependencies, 'get_controller')


class TestDependenciesStructure:
    """Test ExpenseDependencies has proper structure"""

    def test_dependencies_class_exists(self):
        """Test ExpenseDependencies class exists"""
        assert ExpenseDependencies is not None

    def test_dependencies_is_a_class(self):
        """Test ExpenseDependencies is a class"""
        assert isinstance(ExpenseDependencies, type)

    def test_dependencies_has_static_methods(self):
        """Test ExpenseDependencies methods are static"""
        # Both methods should be accessible from class without instance
        assert hasattr(ExpenseDependencies, 'get_repository')
        assert hasattr(ExpenseDependencies, 'get_controller')
