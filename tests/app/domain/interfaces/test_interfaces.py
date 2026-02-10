"""Tests for domain/interfaces/"""

import pytest
from app.domain.interfaces.repository import BaseRepository
from app.domain.interfaces.use_case import IUseCase
from app.domain.interfaces.expense_repository_interface import IExpenseRepository


class TestBaseRepository:
    """Test BaseRepository interface"""

    def test_base_repository_is_abstract_base_class(self):
        """Test BaseRepository is an abstract class"""
        from abc import ABC
        assert issubclass(BaseRepository, ABC)

    def test_base_repository_has_create_method(self):
        """Test BaseRepository has create interface"""
        assert hasattr(BaseRepository, 'create')

    def test_base_repository_has_methods(self):
        """Test BaseRepository defines expected methods"""
        # Should have standard repository methods
        methods = ['create', 'get_all', 'get_by_id', 'update', 'delete']
        for method in methods:
            assert hasattr(BaseRepository, method)


class TestIUseCase:
    """Test IUseCase interface"""

    def test_iusecase_is_abstract(self):
        """Test IUseCase is abstract"""
        from abc import ABC
        assert issubclass(IUseCase, ABC)

    def test_iusecase_has_execute(self):
        """Test IUseCase has execute method"""
        assert hasattr(IUseCase, 'execute')


class TestIExpenseRepository:
    """Test IExpenseRepository interface"""

    def test_iexpense_repository_extends_base(self):
        """Test IExpenseRepository extends BaseRepository"""
        assert issubclass(IExpenseRepository, BaseRepository)

    def test_iexpense_repository_has_get_amounts_and_types(self):
        """Test IExpenseRepository has get_amounts_and_types"""
        assert hasattr(IExpenseRepository, 'get_amounts_and_types')
