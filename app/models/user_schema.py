"""
Pydantic schemas for User API requests and responses.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    nome: str = Field(..., min_length=1, max_length=200, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    senha: str = Field(..., min_length=6, description="User's password")
    data_nascimento: date = Field(..., description="User's birth date (YYYY-MM-DD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "email": "joao@example.com",
                "senha": "senha123!@#",
                "data_nascimento": "1990-05-15"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    nome: Optional[str] = Field(None, min_length=1, max_length=200, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="User's email address")
    data_nascimento: Optional[date] = Field(None, description="User's birth date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva Santos",
                "email": "joao.silva@example.com",
                "data_nascimento": "1990-05-15"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response (read-only)."""
    
    id: str = Field(..., description="Unique identifier")
    nome: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    data_nascimento: date = Field(..., description="User's birth date")
    is_active: bool = Field(True, description="Whether the user account is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "nome": "João Silva",
                "email": "joao@example.com",
                "data_nascimento": "1990-05-15",
                "is_active": True,
                "created_at": "2026-02-19T12:00:00Z",
                "updated_at": "2026-02-19T12:00:00Z"
            }
        }


class UserResponseWithoutPassword(BaseModel):
    """Schema for user response without sensitive data."""
    
    id: str = Field(..., description="Unique identifier")
    nome: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    data_nascimento: date = Field(..., description="User's birth date")
    is_active: bool = Field(True, description="Whether the user account is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        from_attributes = True
