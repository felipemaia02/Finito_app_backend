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
        nome: User's full name
        email: User's email address (unique)
        senha: Hashed password for authentication
        data_nascimento: User's birth date
        is_active: Whether the user account is active
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """

    nome: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address (unique)")
    senha: str = Field(..., min_length=6, description="User's password (should be hashed)")
    data_nascimento: date = Field(..., description="User's birth date")
    is_active: bool = Field(True, description="Whether the user account is active")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "nome": "João Silva",
                "email": "joao@example.com",
                "senha": "hashed_password_hash",
                "data_nascimento": "1990-05-15",
                "is_active": True,
                "created_at": "2026-02-19T12:00:00Z",
                "updated_at": "2026-02-19T12:00:00Z"
            }
        }

    @field_validator("data_nascimento", mode="before")
    @classmethod
    def validate_birth_date(cls, v):
        """Validate that birth date is in the past."""
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace('Z', '+00:00')).date()
        
        today = datetime.now(timezone.utc).date()
        if v >= today:
            raise ValueError("Birth date must be in the past")
        
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError("User must be at least 13 years old")
        
        return v
