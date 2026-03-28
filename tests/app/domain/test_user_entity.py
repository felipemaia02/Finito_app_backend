"""Tests for domain/entities/user_entity.py"""

import pytest
from datetime import date, datetime, timezone
from pydantic import ValidationError
from app.domain.entities.user_entity import User


class TestUserEntity:
    """Test cases for User entity."""

    def test_user_creation_valid(self, sample_user_data):
        """Test creating a valid user entity."""
        user = User(**sample_user_data)
        assert user.id == sample_user_data["id"]
        assert user.name == sample_user_data["name"]
        assert user.email == sample_user_data["email"]
        assert user.is_active is True

    def test_user_with_minimal_data(self):
        """Test creating user with minimal required data."""
        user = User(
            name="John Doe",
            email="john@example.com",
            password="secure_password",
            date_birth=date(1990, 1, 1),
        )
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.is_active is True
        assert user.id is None  # Not set yet

    def test_user_invalid_empty_name(self, sample_user_data):
        """Test that empty name is rejected."""
        sample_user_data["name"] = ""
        with pytest.raises(ValidationError):
            User(**sample_user_data)

    def test_user_invalid_name_too_long(self, sample_user_data):
        """Test that name exceeding max length is rejected."""
        sample_user_data["name"] = "a" * 201
        with pytest.raises(ValidationError):
            User(**sample_user_data)

    def test_user_invalid_email_format(self, sample_user_data):
        """Test that invalid email format is rejected."""
        sample_user_data["email"] = "invalid-email"
        with pytest.raises(ValidationError):
            User(**sample_user_data)

    def test_user_invalid_short_password(self, sample_user_data):
        """Test that password shorter than 6 characters is rejected."""
        sample_user_data["password"] = "pass"
        with pytest.raises(ValidationError):
            User(**sample_user_data)

    def test_user_birth_date_in_future_rejected(self, sample_user_data):
        """Test that future birth date is rejected."""
        sample_user_data["date_birth"] = date.today()
        with pytest.raises(ValueError, match="Birth date must be in the past"):
            User(**sample_user_data)

    def test_user_birth_date_today_rejected(self, sample_user_data):
        """Test that birth date as today is rejected."""
        future_date = datetime.now(timezone.utc).date()
        sample_user_data["date_birth"] = future_date
        with pytest.raises(ValueError, match="Birth date must be in the past"):
            User(**sample_user_data)

    def test_user_too_young_rejected(self, sample_user_data):
        """Test that user under 13 years old is rejected."""
        # Create a date that makes user only 12 years old
        today = datetime.now(timezone.utc).date()
        birth_date = date(today.year - 12, today.month, today.day + 1)
        sample_user_data["date_birth"] = birth_date
        with pytest.raises(ValueError, match="User must be at least 13 years old"):
            User(**sample_user_data)

    def test_user_minimum_age_13_accepted(self):
        """Test that user exactly 13 years old is accepted."""
        today = datetime.now(timezone.utc).date()
        birth_date = date(today.year - 13, today.month, today.day)
        user = User(
            name="Young User",
            email="young@example.com",
            password="password123",
            date_birth=birth_date,
        )
        assert user.date_birth == birth_date

    def test_user_timestamps_auto_set(self):
        """Test that timestamps are automatically set."""
        user = User(
            name="Test User",
            email="test@example.com",
            password="password123",
            date_birth=date(1990, 1, 1),
        )
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_update_timestamp(self, sample_user_entity):
        """Test update_timestamp method."""
        old_timestamp = sample_user_entity.updated_at
        sample_user_entity.update_timestamp()
        assert sample_user_entity.updated_at > old_timestamp

    def test_user_is_active_default_true(self):
        """Test that is_active defaults to True."""
        user = User(
            name="Test User",
            email="test@example.com",
            password="password123",
            date_birth=date(1990, 1, 1),
        )
        assert user.is_active is True

    def test_user_is_active_can_be_set_false(self, sample_user_data):
        """Test that is_active can be set to False."""
        sample_user_data["is_active"] = False
        user = User(**sample_user_data)
        assert user.is_active is False
