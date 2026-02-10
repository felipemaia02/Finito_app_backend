"""
Base entity class for domain entities.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """
    Base class for all domain entities.
    Contains common fields like ID and timestamps.
    """
    
    id: Optional[str] = Field(None, description="Unique identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "created_at": "2026-02-10T12:00:00Z",
                "updated_at": "2026-02-10T12:00:00Z"
            }
        }

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now(timezone.utc)
