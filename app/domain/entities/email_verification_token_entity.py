"""
Email verification token entity.
"""

from datetime import datetime
from pydantic import Field
from app.domain.entities.base_entity import BaseEntity


class EmailVerificationToken(BaseEntity):
    """
    Entity representing a one-time email verification token.

    Attributes:
        user_id: ID of the user this token belongs to
        code_hash: SHA-256 hash of the 6-digit verification code
        expires_at: When the token expires
        is_used: Whether the token has already been consumed
        attempts: Number of failed verification attempts
        resend_count: Number of times a new code has been requested
    """

    user_id: str = Field(..., description="ID of the user this token belongs to")
    code_hash: str = Field(..., description="SHA-256 hash of the verification code")
    expires_at: datetime = Field(..., description="Token expiration datetime")
    is_used: bool = Field(False, description="Whether the token has been consumed")
    attempts: int = Field(0, description="Number of failed verification attempts")
    resend_count: int = Field(0, description="Number of resend requests made")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "code_hash": "a665a45920422f9d417e4867efdc4fb8...",
                "expires_at": "2026-04-23T12:15:00Z",
                "is_used": False,
                "attempts": 0,
                "resend_count": 0,
                "created_at": "2026-04-23T12:00:00Z",
                "updated_at": "2026-04-23T12:00:00Z",
            }
        }
