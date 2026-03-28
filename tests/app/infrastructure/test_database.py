"""Tests for infrastructure/database.py"""

import pytest
from app.infrastructure.database.database import Database


class TestDatabaseInitialization:
    """Test Database class initialization"""

    def test_database_class_exists(self):
        """Test Database class exists"""
        assert Database is not None

    def test_database_has_connect_method(self):
        """Test Database has connect method"""
        assert hasattr(Database, "connect")

    def test_database_has_disconnect_method(self):
        """Test Database has disconnect method"""
        assert hasattr(Database, "disconnect")

    def test_database_has_get_db_method(self):
        """Test Database has get_db method"""
        assert hasattr(Database, "get_db")


class TestDatabaseAttributes:
    """Test Database class attributes"""

    def test_database_has_client_attribute(self):
        """Test Database has _client attribute"""
        assert hasattr(Database, "_client")

    def test_database_has_db_attribute(self):
        """Test Database has _db attribute"""
        assert hasattr(Database, "_db")


class TestDatabaseMethods:
    """Test Database methods exist"""

    def test_database_methods_are_callable(self):
        """Test Database methods are callable"""
        assert callable(Database.connect)
        assert callable(Database.disconnect)


class TestDatabaseGetDbError:
    """Test Database.get_db raises when not initialized."""

    def test_get_db_raises_runtime_error_when_not_initialized(self):
        # Arrange — ensure _db is None
        original_db = Database._db
        Database._db = None

        try:
            # Act / Assert
            with pytest.raises(RuntimeError, match="Database connection not initialized"):
                Database.get_db()
        finally:
            Database._db = original_db

    def test_get_client_raises_runtime_error_when_not_initialized(self):
        # Arrange — ensure _client is None
        original_client = Database._client
        Database._client = None

        try:
            # Act / Assert
            with pytest.raises(RuntimeError, match="Database connection not initialized"):
                Database.get_client()
        finally:
            Database._client = original_client


class TestDatabaseIsConnected:
    """Test Database.is_connected."""

    def test_is_connected_false_when_no_client(self):
        # Arrange
        original_client = Database._client
        original_db = Database._db
        Database._client = None
        Database._db = None

        try:
            # Act / Assert
            assert Database.is_connected() is False
        finally:
            Database._client = original_client
            Database._db = original_db

    def test_is_connected_true_when_both_set(self):
        # Arrange
        from unittest.mock import MagicMock

        original_client = Database._client
        original_db = Database._db
        Database._client = MagicMock()
        Database._db = MagicMock()

        try:
            # Act / Assert
            assert Database.is_connected() is True
        finally:
            Database._client = original_client
            Database._db = original_db


class TestDatabaseConnect:
    """Test Database.connect and disconnect."""

    async def test_connect_sets_client_and_db(self):
        # Arrange
        original_client = Database._client
        original_db = Database._db

        from unittest.mock import MagicMock, AsyncMock, patch

        mock_client = MagicMock()
        mock_client.admin.command = AsyncMock(return_value=True)
        mock_db = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_db)

        try:
            with patch(
                "app.infrastructure.database.database.AsyncIOMotorClient",
                return_value=mock_client,
            ):
                # Act
                await Database.connect()

                # Assert
                assert Database._client is mock_client
        finally:
            Database._client = original_client
            Database._db = original_db

    async def test_connect_raises_when_ping_fails(self):
        # Arrange
        original_client = Database._client
        original_db = Database._db

        from unittest.mock import MagicMock, AsyncMock, patch

        mock_client = MagicMock()
        mock_client.admin.command = AsyncMock(side_effect=RuntimeError("ping failed"))

        try:
            with patch(
                "app.infrastructure.database.database.AsyncIOMotorClient",
                return_value=mock_client,
            ):
                # Act / Assert
                with pytest.raises(RuntimeError, match="ping failed"):
                    await Database.connect()
        finally:
            Database._client = original_client
            Database._db = original_db

    async def test_disconnect_closes_client_when_connected(self):
        # Arrange
        from unittest.mock import MagicMock

        original_client = Database._client
        original_db = Database._db
        mock_client = MagicMock()
        Database._client = mock_client
        Database._db = MagicMock()

        try:
            # Act
            await Database.disconnect()

            # Assert
            mock_client.close.assert_called_once()
            assert Database._db is None
        finally:
            Database._client = original_client
            Database._db = original_db

    async def test_disconnect_does_nothing_when_not_connected(self):
        # Arrange
        original_client = Database._client
        Database._client = None

        try:
            # Act / Assert — should not raise
            await Database.disconnect()
        finally:
            Database._client = original_client
