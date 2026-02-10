"""
Enum definitions for domain entities.
"""

from enum import Enum


class ExpenseCategory(str, Enum):
    """
    Enum for expense categories.
    Each category represents a common expense type.
    """
    
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SHOPPING = "shopping"
    SUBSCRIPTIONS = "subscriptions"
    PERSONAL_CARE = "personal_care"
    HOME = "home"
    BILLS = "bills"
    WORK = "work"
    GIFTS = "gifts"
    INSURANCE = "insurance"
    SAVINGS = "savings"
    INVESTMENTS = "investments"
    PET = "pet"
    GROCERIES = "groceries"
    RESTAURANTS = "restaurants"
    GAS = "gas"
    CAR = "car"
    OTHER = "other"
    
    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value
