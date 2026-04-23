"""Expense routes with class-based views using fastapi-utils."""

from fastapi import APIRouter, Depends, Security, HTTPException, status
from typing import List

from fastapi_utils.cbv import cbv

from app.controllers.expense_controller import ExpenseController
from app.infrastructure.dependencies.expense_dependencies import ExpenseDependencies
from app.infrastructure.dependencies.oauth2_dependencies import verify_oauth2_token
from app.infrastructure.dependencies.auth_dependencies import verify_api_key
from app.models.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.models.auth_schema import TokenData
from app.models.response_schema import StandardResponse
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(tags=["expenses"])


@cbv(router)
class ExpenseViews:
    """Class-based views for expense operations using fastapi-utils."""

    controller: ExpenseController = Depends(ExpenseDependencies.get_controller)
    current_user: TokenData = Security(verify_oauth2_token)
    api_key: str = Security(verify_api_key)

    @router.post(
        "/expenses",
        response_model=StandardResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_expense(self, expense_data: ExpenseCreate) -> StandardResponse:
        """Create a new expense in a group (user must be a group member)."""
        try:
            await self.controller.create_expense(expense_data, self.current_user.sub)
            return StandardResponse(message="Expense created successfully")
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating expense: {str(e)}",
            )

    @router.get("/expenses/{group_id}", response_model=List[ExpenseResponse])
    async def list_all_expenses(
        self,
        group_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ExpenseResponse]:
        """Get all expenses for a group (user must be a group member)."""
        try:
            return await self.controller.get_all_expenses(group_id, self.current_user.sub, skip, limit)
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error fetching expenses for group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching expenses: {str(e)}",
            )

    @router.get("/expenses/{expense_id}/details", response_model=ExpenseResponse)
    async def get_expense_details(self, expense_id: str) -> ExpenseResponse:
        """Get a specific expense by ID (user must be a member of the expense's group)."""
        try:
            expense = await self.controller.get_expense_by_id(expense_id, self.current_user.sub)
            if not expense:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense {expense_id} not found",
                )
            return expense
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error fetching expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching expense: {str(e)}",
            )

    @router.patch("/expenses/{expense_id}", response_model=StandardResponse)
    async def update_expense(
        self,
        expense_id: str,
        expense_data: ExpenseUpdate,
    ) -> StandardResponse:
        """Update an existing expense (user must be a member of the expense's group)."""
        try:
            updated_expense = await self.controller.update_expense(
                expense_id, expense_data, self.current_user.sub
            )
            if not updated_expense:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense {expense_id} not found",
                )
            return StandardResponse(message="Expense updated successfully")
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating expense: {str(e)}",
            )

    @router.delete("/expenses/{expense_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
    async def delete_expense(self, expense_id: str) -> StandardResponse:
        """Delete an expense (user must be a member of the expense's group)."""
        try:
            result = await self.controller.delete_expense(expense_id, self.current_user.sub)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense {expense_id} not found",
                )
            return StandardResponse(message="Expense deleted successfully")
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting expense: {str(e)}",
            )

    @router.get("/expenses/{group_id}/analytics", response_model=List[dict])
    async def get_expense_analytics(self, group_id: str) -> List[dict]:
        """Get analytics data (amounts and types) for a group (user must be a member)."""
        try:
            return await self.controller.get_amounts_and_types(group_id, self.current_user.sub)
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error fetching analytics for group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching analytics: {str(e)}",
            )
