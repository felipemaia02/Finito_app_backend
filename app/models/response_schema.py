"""Standard response model for non-GET endpoints."""

from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    """Generic success response returned by create, update, and delete endpoints."""

    status: str = Field(default="ok", description="Operation status")
    message: str = Field(..., description="Human-readable result message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "message": "Operation completed successfully",
            }
        }
