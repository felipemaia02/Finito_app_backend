"""
Pydantic schemas for Expense API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType


class ExpenseCreate(BaseModel):
    """Schema for creating a new expense."""
    
    group_id: str = Field(..., min_length=1, description="ID of the expense group")
    amount_cents: int = Field(..., gt=0, description="Amount in cents (e.g., 1000 = $10.00)")
    category: ExpenseCategory = Field(..., description="Expense category")
    type_expense: ExpenseType = Field(..., description="Payment method type")
    spent_by: str = Field(..., min_length=1, max_length=100, description="Person/entity who spent")
    date: Optional[datetime] = Field(None, description="Date of expense (defaults to now)")
    note: Optional[str] = Field(None, max_length=500, description="Optional note about the expense")
    
    class Config:
        json_schema_extra = {
            "example": {
                "group_id": "507f1f77bcf86cd799439012",
                "amount_cents": 2500,
                "category": "food",
                "type_expense": "credit_card",
                "spent_by": "John Doe",
                "date": "2026-02-10T12:00:00Z",
                "note": "Lunch at downtown restaurant"
            }
        }


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense."""
    
    amount_cents: Optional[int] = Field(None, gt=0, description="Amount in cents")
    category: Optional[ExpenseCategory] = Field(None, description="Expense category")
    type_expense: Optional[ExpenseType] = Field(None, description="Payment method type")
    spent_by: Optional[str] = Field(None, min_length=1, max_length=100, description="Person/entity who spent")
    date: Optional[datetime] = Field(None, description="Date of expense")
    note: Optional[str] = Field(None, max_length=500, description="Optional note")
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount_cents": 3000,
                "category": "dining",
                "note": "Updated note"
            }
        }


class ExpenseResponse(BaseModel):
    """Schema for expense response (read-only)."""
    
    id: str = Field(..., description="Unique identifier")
    group_id: str = Field(..., description="ID of the expense group")
    amount_cents: int = Field(..., description="Amount in cents")
    category: ExpenseCategory = Field(..., description="Expense category")
    type_expense: ExpenseType = Field(..., description="Payment method type")
    spent_by: str = Field(..., description="Person/entity who spent")
    date: datetime = Field(..., description="Date of expense")
    note: Optional[str] = Field(None, description="Optional note")
    is_deleted: bool = Field(False, description="Soft delete flag")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "group_id": "507f1f77bcf86cd799439012",
                "amount_cents": 2500,
                "category": "food",
                "type_expense": "credit_card",
                "spent_by": "John Doe",
                "date": "2026-02-10T12:00:00Z",
                "note": "Lunch at downtown restaurant",
                "is_deleted": False,
                "created_at": "2026-02-10T12:00:00Z",
                "updated_at": "2026-02-10T12:00:00Z"
            }
        }
