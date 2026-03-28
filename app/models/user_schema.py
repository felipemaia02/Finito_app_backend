"""
Pydantic schemas for User API requests and responses.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")
    date_birth: date = Field(..., description="User's birth date (YYYY-MM-DD)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Silva",
                "email": "john@example.com",
                "password": "password123!@#",
                "date_birth": "1990-05-15",
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="User's full name"
    )
    email: Optional[EmailStr] = Field(None, description="User's email address")
    date_birth: Optional[date] = Field(None, description="User's birth date")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Silva Santos",
                "email": "john.silva@example.com",
                "date_birth": "1990-05-15",
            }
        }


class UserResponse(BaseModel):
    """Schema for user response (read-only)."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    date_birth: date = Field(..., description="User's birth date")
    is_active: bool = Field(True, description="Whether the user account is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "John Silva",
                "email": "john@example.com",
                "date_birth": "1990-05-15",
                "is_active": True,
                "created_at": "2026-02-19T12:00:00Z",
                "updated_at": "2026-02-19T12:00:00Z",
            }
        }


class UserResponseWithoutPassword(BaseModel):
    """Schema for user response without sensitive data."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    date_birth: date = Field(..., description="User's birth date")
    is_active: bool = Field(True, description="Whether the user account is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        populate_by_name = True
        from_attributes = True
