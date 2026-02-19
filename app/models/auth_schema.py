"""
Pydantic schemas for Authentication/OAuth2.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    email: EmailStr = Field(..., description="User's email address")
    senha: str = Field(..., description="User's password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao@example.com",
                "senha": "senha123!@#"
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: datetime = Field(..., description="Token expiration datetime")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "expires_at": "2026-02-19T12:00:00"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenValidationResponse(BaseModel):
    """Schema for token validation response."""
    
    valid: bool = Field(..., description="Whether token is valid")
    email: Optional[str] = Field(None, description="User email from token")
    expires_at: Optional[datetime] = Field(None, description="Token expiration datetime")
    
    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "email": "joao@example.com",
                "expires_at": "2026-02-19T12:00:00"
            }
        }


class TokenData(BaseModel):
    """Schema for token payload data."""
    
    sub: str = Field(..., description="Subject - typically user email")
    exp: Optional[int] = Field(None, description="Expiration time")
    type: str = Field(default="access", description="Token type (access or refresh)")
