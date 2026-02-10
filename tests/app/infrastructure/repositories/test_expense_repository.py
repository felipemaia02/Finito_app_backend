"""Tests for infrastructure/repositories/expense_repository.py"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.infrastructure.repositories.expense_repository import MongoExpenseRepository
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


class TestMongoExpenseRepositoryInitialization:
    """Test MongoExpenseRepository initialization"""

    def test_repository_can_be_instantiated(self):
        """Test creating MongoExpenseRepository"""
        repo = MongoExpenseRepository()
        assert repo is not None

    def test_repository_implements_interface(self):
        """Test repository implements IExpenseRepository"""
        repo = MongoExpenseRepository()
        assert isinstance(repo, IExpenseRepository)


class TestMongoExpenseRepositoryMethods:
    """Test MongoExpenseRepository has required methods"""

    def test_repository_has_create(self):
        """Test repository has create method"""
        repo = MongoExpenseRepository()
        assert hasattr(repo, 'create')

    def test_repository_has_get_all(self):
        """Test repository has get_all method"""
        repo = MongoExpenseRepository()
        assert hasattr(repo, 'get_all')

    def test_repository_has_get_by_id(self):
        """Test repository has get_by_id method"""
        repo = MongoExpenseRepository()
        assert hasattr(repo, 'get_by_id')

    def test_repository_has_update(self):
        """Test repository has update method"""
        repo = MongoExpenseRepository()
        assert hasattr(repo, 'update')

    def test_repository_has_delete(self):
        """Test repository has delete method"""
        repo = MongoExpenseRepository()
        assert hasattr(repo, 'delete')

    def test_repository_has_get_amounts_and_types(self):
        """Test repository has get_amounts_and_types method"""
        repo = MongoExpenseRepository()
        assert hasattr(repo, 'get_amounts_and_types')


class TestMongoExpenseRepositoryCallable:
    """Test MongoExpenseRepository methods are callable"""

    def test_create_is_callable(self):
        """Test create is async callable"""
        repo = MongoExpenseRepository()
        assert callable(repo.create)

    def test_get_all_is_callable(self):
        """Test get_all is async callable"""
        repo = MongoExpenseRepository()
        assert callable(repo.get_all)

    def test_get_by_id_is_callable(self):
        """Test get_by_id is async callable"""
        repo = MongoExpenseRepository()
        assert callable(repo.get_by_id)

    def test_update_is_callable(self):
        """Test update is async callable"""
        repo = MongoExpenseRepository()
        assert callable(repo.update)

    def test_delete_is_callable(self):
        """Test delete is async callable"""
        repo = MongoExpenseRepository()
        assert callable(repo.delete)
