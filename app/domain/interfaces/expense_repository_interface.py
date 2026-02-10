"""
Expense repository interface for expense-specific operations.
"""

from typing import List, Dict
from abc import abstractmethod
from app.domain.interfaces.repository import BaseRepository
from app.domain.entities.expense_entity import Expense


class IExpenseRepository(BaseRepository[Expense]):
    """
    Interface for expense repository operations.
    Extends the base repository with expense-specific queries.
    """
    
    @abstractmethod
    async def get_all(self, group_id: str, skip: int = 0, limit: int = 100) -> List[Expense]:
        """
        Get all expenses for a specific group (from all participants).
        Allows retrieving expenses added by multiple people to the same group.
        
        Args:
            group_id: ID of the expense group
            skip: Number of expenses to skip for pagination
            limit: Maximum number of expenses to return
            
        Returns:
            List of all expenses in the group regardless of who added them
        """
        pass
    
    @abstractmethod
    async def get_amounts_and_types(self, group_id: str) -> List[Dict[str, any]]:
        """
        Get only amount_cents and type_expense for all expenses in a group.
        Useful for analytics and reports without loading full expense data.
        Includes expenses from all participants in the group.
        
        Args:
            group_id: ID of the expense group
            
        Returns:
            List of dictionaries containing only amount_cents and type_expense
            Example: [{"amount_cents": 2500, "type_expense": "credit_card"}, ...]
        """
        pass
