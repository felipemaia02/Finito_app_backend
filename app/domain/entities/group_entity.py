"""Group entity representing a group of users that share expenses."""

from typing import List
from pydantic import Field
from app.domain.entities.base_entity import BaseEntity


class Group(BaseEntity):
    """
    Group entity representing a group of users.

    Attributes:
        id: Unique identifier (MongoDB ObjectId as string)
        group_name: Name of the group
        user_ids: List of user IDs that belong to this group
        is_deleted: Soft delete flag
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """

    group_name: str = Field(
        ..., min_length=1, max_length=200, description="Name of the group"
    )
    creator_id: str = Field(
        ..., min_length=1, description="User ID of the group creator"
    )
    user_ids: List[str] = Field(
        default_factory=list, description="List of user IDs belonging to this group"
    )
    is_deleted: bool = Field(False, description="Soft delete flag")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "group_name": "Viagem Europa 2026",
                "creator_id": "507f1f77bcf86cd799439012",
                "user_ids": [
                    "507f1f77bcf86cd799439012",
                    "507f1f77bcf86cd799439013",
                ],
                "is_deleted": False,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            }
        }
