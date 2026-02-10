"""Dependency injection container for expense operations."""

from fastapi import Depends

from app.controllers.expense_controller import ExpenseController
from app.domain.interfaces.expense_repository_interface import IExpenseRepository
from app.infrastructure.repositories.expense_repository import MongoExpenseRepository


class ExpenseDependencies:
    """Container for managing expense-related dependencies."""

    @staticmethod
    def get_repository() -> IExpenseRepository:
        """
        Provides the expense repository instance.
        
        Returns:
            IExpenseRepository: MongoDB implementation of expense repository
        """
        return MongoExpenseRepository()

    @staticmethod
    def get_controller(
        repository: IExpenseRepository = Depends(get_repository.__func__),
    ) -> ExpenseController:
        """
        Provides the expense controller instance with injected repository.
        
        Args:
            repository: Injected expense repository
            
        Returns:
            ExpenseController: Controller instance with repository
        """
        return ExpenseController(repository)
