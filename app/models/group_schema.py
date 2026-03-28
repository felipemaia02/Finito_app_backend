"""Pydantic schemas for Group API requests and responses."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.user_schema import UserResponse


class GroupCreate(BaseModel):
    """Schema for creating a new group."""

    group_name: str = Field(
        ..., min_length=1, max_length=200, description="Name of the group"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "group_name": "Viagem Europa 2026",
            }
        }


class GroupUpdate(BaseModel):
    """Schema for updating a group."""

    group_name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New name of the group"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "group_name": "Viagem Europa 2027",
            }
        }


class AddUserRequest(BaseModel):
    """Schema for adding a user to a group."""

    user_id: str = Field(..., min_length=1, description="ID of the user to add")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439012",
            }
        }


class GroupResponse(BaseModel):
    """Schema for group response with populated user objects."""

    id: str = Field(..., description="Unique identifier")
    group_name: str = Field(..., description="Name of the group")
    users: List[UserResponse] = Field(
        default_factory=list, description="List of users belonging to this group"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "group_name": "Viagem Europa 2026",
                "users": [],
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            }
        }
