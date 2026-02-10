"""Tests for infrastructure/database.py"""

import pytest
from app.infrastructure.database import Database


class TestDatabaseInitialization:
    """Test Database class initialization"""

    def test_database_class_exists(self):
        """Test Database class exists"""
        assert Database is not None

    def test_database_has_connect_method(self):
        """Test Database has connect method"""
        assert hasattr(Database, 'connect')

    def test_database_has_disconnect_method(self):
        """Test Database has disconnect method"""
        assert hasattr(Database, 'disconnect')

    def test_database_has_get_db_method(self):
        """Test Database has get_db method"""
        assert hasattr(Database, 'get_db')


class TestDatabaseAttributes:
    """Test Database class attributes"""

    def test_database_has_client_attribute(self):
        """Test Database has _client attribute"""
        assert hasattr(Database, '_client')

    def test_database_has_db_attribute(self):
        """Test Database has _db attribute"""
        assert hasattr(Database, '_db')


class TestDatabaseMethods:
    """Test Database methods exist"""

    def test_database_methods_are_callable(self):
        """Test Database methods are callable"""
        assert callable(Database.connect)
        assert callable(Database.disconnect)

