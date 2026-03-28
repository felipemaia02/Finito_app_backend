"""Tests for models/user_schema.py"""

import pytest
from datetime import date, datetime, timezone
from pydantic import ValidationError
from bson import ObjectId

from app.models.user_schema import UserCreate, UserUpdate, UserResponse


class TestUserCreateSchema:
    """Test UserCreate Pydantic schema."""

    def test_create_with_required_fields(self):
        # Arrange & Act
        schema = UserCreate(
            name="John Silva",
            email="john@example.com",
            password="password123",
            date_birth=date(1990, 5, 15),
        )

        # Assert
        assert schema.name == "John Silva"
        assert schema.email == "john@example.com"
        assert schema.date_birth == date(1990, 5, 15)

    def test_create_invalid_email_raises(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            UserCreate(
                name="John",
                email="not-an-email",
                password="password123",
                date_birth=date(1990, 5, 15),
            )

    def test_create_short_password_raises(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            UserCreate(
                name="John",
                email="john@example.com",
                password="12345",  # < 6 chars
                date_birth=date(1990, 5, 15),
            )

    def test_create_empty_name_raises(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            UserCreate(
                name="",
                email="john@example.com",
                password="password123",
                date_birth=date(1990, 5, 15),
            )

    def test_create_name_too_long_raises(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            UserCreate(
                name="a" * 201,
                email="john@example.com",
                password="password123",
                date_birth=date(1990, 5, 15),
            )

    def test_create_can_serialize(self):
        # Arrange
        schema = UserCreate(
            name="John Silva",
            email="john@example.com",
            password="password123",
            date_birth=date(1990, 5, 15),
        )

        # Act
        data = schema.model_dump()

        # Assert
        assert "name" in data
        assert "email" in data
        assert "password" in data
        assert "date_birth" in data


class TestUserUpdateSchema:
    """Test UserUpdate Pydantic schema."""

    def test_update_with_no_fields(self):
        # Arrange & Act
        schema = UserUpdate()

        # Assert
        assert schema.name is None
        assert schema.email is None
        assert schema.date_birth is None

    def test_update_with_partial_fields(self):
        # Arrange & Act
        schema = UserUpdate(name="New Name")

        # Assert
        assert schema.name == "New Name"
        assert schema.email is None

    def test_update_invalid_email_raises(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            UserUpdate(email="not-valid-email")

    def test_update_empty_name_raises(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            UserUpdate(name="")

    def test_update_serializes_only_set_fields(self):
        # Arrange
        schema = UserUpdate(name="Updated")

        # Act
        data = schema.model_dump(exclude_unset=True)

        # Assert
        assert "name" in data
        assert "email" not in data


class TestUserResponseSchema:
    """Test UserResponse Pydantic schema."""

    def test_response_created_correctly(self):
        # Arrange & Act
        schema = UserResponse(
            id=str(ObjectId()),
            name="John Silva",
            email="john@example.com",
            date_birth=date(1990, 5, 15),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Assert
        assert schema.name == "John Silva"
        assert schema.is_active is True

    def test_response_missing_required_field_raises(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            UserResponse(
                name="John",
                email="john@example.com",
                # missing id, date_birth, created_at, updated_at
            )

    def test_response_can_serialize(self):
        # Arrange
        now = datetime.now(timezone.utc)
        schema = UserResponse(
            id=str(ObjectId()),
            name="John",
            email="john@example.com",
            date_birth=date(1990, 1, 1),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        # Act
        data = schema.model_dump()

        # Assert
        assert data["name"] == "John"
        assert data["is_active"] is True
