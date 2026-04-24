"""
User entity for user management.
"""

from datetime import datetime, timezone, date
from pydantic import Field, field_validator, EmailStr
from app.domain.entities.base_entity import BaseEntity


class User(BaseEntity):
    """
    User entity representing a registered user in the system.

    Attributes:
        id: Unique identifier (MongoDB ObjectId as string)
        name: User's full name
        email: User's email address (unique)
        password: Hashed password for authentication
        date_birth: User's birth date
        is_active: Whether the user account is active
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """

    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address (unique)")
    password: str = Field(
        ..., min_length=6, description="User's password (should be hashed)"
    )
    date_birth: date = Field(..., description="User's birth date")
    is_active: bool = Field(False, description="Whether the user account is active")
    is_email_verified: bool = Field(False, description="Whether the user's email has been verified")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "John Silva",
                "email": "john@example.com",
                "password": "hashed_password_hash",
                "date_birth": "1990-05-15",
                "is_active": False,
                "is_email_verified": False,
                "created_at": "2026-02-19T12:00:00Z",
                "updated_at": "2026-02-19T12:00:00Z",
            }
        }

    @field_validator("date_birth", mode="before")
    @classmethod
    def validate_birth_date(cls, v):
        """Validate that birth date is in the past."""
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00")).date()

        today = datetime.now(timezone.utc).date()
        if v >= today:
            raise ValueError("Birth date must be in the past")

        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError("User must be at least 13 years old")

        return v
