"""
Expense type enumeration for payment methods.
"""

from enum import Enum


class ExpenseType(str, Enum):
    """
    Enum for expense payment types.
    Each type represents a payment method.
    """
    
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX_TRANSFER = "pix_transfer"
    CASH = "cash"
    
    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value
