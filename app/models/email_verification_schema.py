"""
Pydantic schemas for email verification API.
"""

from pydantic import BaseModel, EmailStr, Field


class VerifyEmailRequest(BaseModel):
    """Body for POST /auth/verify-email."""

    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

    class Config:
        json_schema_extra = {"example": {"code": "382910"}}


class UserRegisterResponse(BaseModel):
    """Response returned after a successful registration."""

    message: str = Field(..., description="Human-readable status message")
    verification_token: str = Field(
        ..., description="Short-lived JWT to be sent on the verify-email endpoint"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "User registered successfully. Check your email for the verification code.",
                "verification_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }


class RequestVerificationRequest(BaseModel):
    """Body for POST /auth/request-verification."""

    email: EmailStr = Field(..., description="Email of the registered but unverified account")

    class Config:
        json_schema_extra = {"example": {"email": "user@example.com"}}
