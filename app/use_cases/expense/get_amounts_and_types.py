"""Get Amounts and Types use case."""

from typing import List, Dict
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase

logger = get_logger(__name__)


class GetAmountsAndTypesUseCase(IUseCase[str, List[Dict[str, any]]]):
    """Use case for retrieving optimized analytics data for a group."""
    
    def __init__(self, repository: IExpenseRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IExpenseRepository
        """
        self.repository = repository
    
    async def execute(self, group_id: str) -> List[Dict[str, any]]:
        """
        Get optimized data with only amount_cents and type_expense for group analytics.
        Includes data from all participants in the group.
        
        Args:
            group_id: ID of the expense group
            
        Returns:
            List of dictionaries with amount_cents and type_expense from all participants
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Fetching amounts and types for group: {group_id}")
            
            data = await self.repository.get_amounts_and_types(group_id)
            
            logger.info(f"Retrieved {len(data)} expense amounts and types for group: {group_id}")
            return data
        except Exception as e:
            logger.error(f"Error fetching amounts and types for group {group_id}: {e}")
            raise
