"""Expense routes with class-based views using fastapi-utils."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from fastapi_utils.cbv import cbv

from app.controllers.expense_controller import ExpenseController
from app.infrastructure.dependencies import ExpenseDependencies
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(tags=["expenses"])


@cbv(router)
class ExpenseViews:
    """Class-based views for expense operations using fastapi-utils."""

    controller: ExpenseController = Depends(ExpenseDependencies.get_controller)

    @router.post(
        "/expenses",
        response_model=ExpenseResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_expense(self, expense_data: ExpenseCreate) -> ExpenseResponse:
        """
        Create a new expense in a group.
        
        Args:
            expense_data: Expense creation data
            
        Returns:
            Created expense response with ID
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            return await self.controller.create_expense(expense_data)
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating expense: {str(e)}"
            )

    @router.get("/expenses/{group_id}", response_model=List[ExpenseResponse])
    async def list_all_expenses(
        self,
        group_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ExpenseResponse]:
        """
        Get all expenses for a group.
        
        Args:
            group_id: ID of the expense group
            skip: Number of items to skip (pagination)
            limit: Maximum number of items to return
            
        Returns:
            List of expenses from all participants in the group
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            return await self.controller.get_all_expenses(group_id, skip, limit)
        except Exception as e:
            logger.error(f"Error fetching expenses for group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching expenses: {str(e)}"
            )

    @router.get("/expenses/{expense_id}/details", response_model=ExpenseResponse)
    async def get_expense_details(self, expense_id: str) -> ExpenseResponse:
        """
        Get a specific expense by ID.
        
        Args:
            expense_id: ID of the expense
            
        Returns:
            Expense details
            
        Raises:
            HTTPException: If expense not found
        """
        try:
            expense = await self.controller.get_expense_by_id(expense_id)
            if not expense:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense {expense_id} not found"
                )
            return expense
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching expense: {str(e)}"
            )

    @router.patch("/expenses/{expense_id}", response_model=ExpenseResponse)
    async def update_expense(
        self,
        expense_id: str,
        expense_data: ExpenseUpdate,
    ) -> ExpenseResponse:
        """
        Update an existing expense (partial update).
        
        Args:
            expense_id: ID of the expense to update
            expense_data: Fields to update
            
        Returns:
            Updated expense response
            
        Raises:
            HTTPException: If expense not found or update fails
        """
        try:
            updated_expense = await self.controller.update_expense(expense_id, expense_data)
            if not updated_expense:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense {expense_id} not found"
                )
            return updated_expense
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating expense: {str(e)}"
            )

    @router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_expense(self, expense_id: str) -> None:
        """
        Delete (soft delete) an expense.
        
        Args:
            expense_id: ID of the expense to delete
            
        Raises:
            HTTPException: If expense not found or deletion fails
        """
        try:
            result = await self.controller.delete_expense(expense_id)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense {expense_id} not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting expense: {str(e)}"
            )

    @router.get("/expenses/{group_id}/analytics", response_model=List[dict])
    async def get_expense_analytics(self, group_id: str) -> List[dict]:
        """
        Get analytics data (amounts and types) for a group.
        Optimized projection for summary calculations.
        
        Args:
            group_id: ID of the expense group
            
        Returns:
            List of dictionaries with amount_cents and type_expense
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            return await self.controller.get_amounts_and_types(group_id)
        except Exception as e:
            logger.error(f"Error fetching analytics for group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching analytics: {str(e)}"
            )

