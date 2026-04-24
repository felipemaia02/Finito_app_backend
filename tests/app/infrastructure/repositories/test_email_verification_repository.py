"""Tests for infrastructure/repositories/email_verification_repository.py"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from app.infrastructure.repositories.email_verification_repository import (
    MongoEmailVerificationRepository,
)
from app.domain.interfaces.email_verification_repository_interface import (
    IEmailVerificationRepository,
)
from app.domain.entities.email_verification_token_entity import EmailVerificationToken


def make_token_doc(token_id=None):
    """Create a sample email verification token document."""
    import hashlib

    oid = ObjectId(token_id) if token_id else ObjectId()
    return {
        "_id": oid,
        "user_id": str(ObjectId()),
        "code_hash": hashlib.sha256(b"382910").hexdigest(),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15),
        "is_used": False,
        "attempts": 0,
        "resend_count": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def make_token_entity():
    """Create a sample EmailVerificationToken entity."""
    import hashlib

    return EmailVerificationToken(
        user_id=str(ObjectId()),
        code_hash=hashlib.sha256(b"382910").hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )


class TestMongoEmailVerificationRepositoryInit:
    def test_repository_is_instance_of_interface(self):
        # Arrange / Act
        repo = MongoEmailVerificationRepository()

        # Assert
        assert isinstance(repo, IEmailVerificationRepository)

    def test_collection_name_is_correct(self):
        # Arrange / Act
        repo = MongoEmailVerificationRepository()

        # Assert
        assert repo.collection_name == "email_verification_tokens"


class TestMongoEmailVerificationRepositoryDocumentConversion:
    def test_entity_to_document_without_id(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        entity = make_token_entity()

        # Act
        doc = repo._entity_to_document(entity)

        # Assert
        assert "_id" in doc
        assert "user_id" in doc
        assert "code_hash" in doc
        assert "is_used" in doc
        assert "id" not in doc

    def test_entity_to_document_with_existing_id(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        existing_id = str(ObjectId())
        entity = make_token_entity()
        entity.id = existing_id

        # Act
        doc = repo._entity_to_document(entity)

        # Assert
        assert doc["_id"] == ObjectId(existing_id)

    def test_document_to_entity_converts_id(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        doc = make_token_doc()
        original_id = str(doc["_id"])

        # Act
        entity = repo._document_to_entity(doc)

        # Assert
        assert entity is not None
        assert isinstance(entity, EmailVerificationToken)
        assert entity.id == original_id
        assert entity.user_id == doc["user_id"]

    def test_document_to_entity_none_returns_none(self):
        # Arrange
        repo = MongoEmailVerificationRepository()

        # Act
        result = repo._document_to_entity(None)

        # Assert
        assert result is None

    def test_document_to_entity_preserves_fields(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        doc = make_token_doc()
        doc["attempts"] = 2
        doc["resend_count"] = 1
        doc["is_used"] = True

        # Act
        entity = repo._document_to_entity(doc)

        # Assert
        assert entity.attempts == 2
        assert entity.resend_count == 1
        assert entity.is_used is True


class TestMongoEmailVerificationRepositoryCreate:
    async def test_create_success(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        entity = make_token_entity()
        inserted_id = ObjectId()
        mock_col = MagicMock()
        mock_col.insert_one = AsyncMock(return_value=MagicMock(inserted_id=inserted_id))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.create(entity)

        # Assert
        assert result.id == str(inserted_id)
        mock_col.insert_one.assert_called_once()

    async def test_create_propagates_exception(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        entity = make_token_entity()
        mock_col = MagicMock()
        mock_col.insert_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError, match="DB error"):
                await repo.create(entity)


class TestMongoEmailVerificationRepositoryGetById:
    async def test_get_by_id_found(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        doc = make_token_doc()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=doc)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_by_id(str(doc["_id"]))

        # Assert
        assert result is not None
        assert isinstance(result, EmailVerificationToken)

    async def test_get_by_id_not_found_returns_none(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=None)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_by_id(str(ObjectId()))

        # Assert
        assert result is None

    async def test_get_by_id_propagates_exception(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.get_by_id(str(ObjectId()))


class TestMongoEmailVerificationRepositoryGetValidToken:
    async def test_get_valid_token_found(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        doc = make_token_doc()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=doc)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_valid_token_by_user_id("user-123")

        # Assert
        assert result is not None
        assert isinstance(result, EmailVerificationToken)

    async def test_get_valid_token_not_found_returns_none(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=None)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_valid_token_by_user_id("user-123")

        # Assert
        assert result is None

    async def test_get_valid_token_propagates_exception(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.get_valid_token_by_user_id("user-123")


class TestMongoEmailVerificationRepositoryGetLatest:
    async def test_get_latest_found(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        doc = make_token_doc()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=doc)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_latest_by_user_id("user-123")

        # Assert
        assert result is not None
        assert isinstance(result, EmailVerificationToken)

    async def test_get_latest_not_found_returns_none(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.find_one = AsyncMock(return_value=None)

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.get_latest_by_user_id("user-123")

        # Assert
        assert result is None


class TestMongoEmailVerificationRepositoryMarkAsUsed:
    async def test_mark_as_used_success(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        token_id = str(ObjectId())
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock()

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            await repo.mark_as_used(token_id)

        # Assert
        mock_col.update_one.assert_called_once()
        call_args = mock_col.update_one.call_args
        assert call_args[0][1]["$set"]["is_used"] is True

    async def test_mark_as_used_propagates_exception(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.mark_as_used(str(ObjectId()))


class TestMongoEmailVerificationRepositoryIncrementAttempts:
    async def test_increment_attempts_success(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        token_id = str(ObjectId())
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock()

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            await repo.increment_attempts(token_id)

        # Assert
        mock_col.update_one.assert_called_once()
        call_args = mock_col.update_one.call_args
        assert "$inc" in call_args[0][1]
        assert call_args[0][1]["$inc"]["attempts"] == 1

    async def test_increment_attempts_propagates_exception(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.increment_attempts(str(ObjectId()))


class TestMongoEmailVerificationRepositoryInvalidateAll:
    async def test_invalidate_all_calls_update_many(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.update_many = AsyncMock()

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            await repo.invalidate_all_by_user_id("user-123")

        # Assert
        mock_col.update_many.assert_called_once()
        call_args = mock_col.update_many.call_args
        assert call_args[0][0]["user_id"] == "user-123"
        assert call_args[0][1]["$set"]["is_used"] is True

    async def test_invalidate_all_propagates_exception(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.update_many = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.invalidate_all_by_user_id("user-123")


class TestMongoEmailVerificationRepositoryDelete:
    async def test_delete_marks_as_used(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        token_id = str(ObjectId())
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(return_value=MagicMock(modified_count=1))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.delete(token_id)

        # Assert
        assert result is True
        mock_col.update_one.assert_called_once()

    async def test_delete_returns_false_when_not_found(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(return_value=MagicMock(modified_count=0))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act
            result = await repo.delete(str(ObjectId()))

        # Assert
        assert result is False

    async def test_delete_propagates_exception(self):
        # Arrange
        repo = MongoEmailVerificationRepository()
        mock_col = MagicMock()
        mock_col.update_one = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch.object(repo, "_get_collection", return_value=mock_col):
            # Act / Assert
            with pytest.raises(RuntimeError):
                await repo.delete(str(ObjectId()))
