"""
Expense entity for financial tracking.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import Field, field_validator
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums.expense_category_enum import ExpenseCategory
from app.domain.enums.expense_type_enum import ExpenseType


class Expense(BaseEntity):
    """
    Expense entity representing a financial transaction.
    
    Attributes:
        id: Unique identifier (MongoDB ObjectId as string)
        group_id: ID of the expense group (multiple participants can contribute)
        amount_cents: Amount in cents (e.g., 1000 = $10.00)
        category: Category of the expense
        type_expense: Payment method type (credit card, debit card, pix/transfer, cash)
        spent_by: Person/entity name who made the expense
        date: Date when the expense was made
        note: Optional note about the expense
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """

    group_id: str = Field(..., min_length=1, description="ID of the expense group")
    amount_cents: int = Field(..., gt=0, description="Amount in cents (must be positive)")
    category: ExpenseCategory = Field(..., description="Expense category")
    type_expense: ExpenseType = Field(..., description="Payment method type")
    spent_by: str = Field(..., min_length=1, max_length=100, description="Person/entity who spent")
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date of expense")
    note: Optional[str] = Field(None, max_length=500, description="Optional note about the expense")
    is_deleted: bool = Field(False, description="Soft delete flag - True if expense is deleted logically")

    class Config:
        populate_by_name = True
        use_enum_values = True
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

    @field_validator("amount_cents")
    @classmethod
    def validate_amount(cls, v: int) -> int:
        """Validate that amount is a positive integer in cents."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > 9999999:
            raise ValueError("Amount exceeds maximum allowed value")
        return v

    @property
    def amount_decimal(self) -> float:
        """Convert cents to base unit (decimal) for display."""
        return self.amount_cents / 100

    @staticmethod
    def from_decimal(amount: float) -> int:
        """Convert decimal amount to cents for storage."""
        return int(round(amount * 100))

    def __str__(self) -> str:
        """String representation of expense."""
        return f"{self.amount_decimal:.2f} - {self.category.value} ({self.spent_by})"
