"""User routes with class-based views using fastapi-utils."""

from fastapi import APIRouter, Depends, Security, HTTPException, status
from typing import List

from fastapi_utils.cbv import cbv

from app.controllers.user_controller import UserController
from app.infrastructure.user_dependencies import UserDependencies
from app.infrastructure.auth_dependencies import verify_api_key
from app.models.user_schema import UserCreate, UserUpdate, UserResponse
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(tags=["users"], prefix="/users")


@cbv(router)
class UserViews:
    """Class-based views for user operations using fastapi-utils."""

    controller: UserController = Depends(UserDependencies.get_controller)
    api_key: str = Security(verify_api_key)

    @router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user in the system.
        
        Args:
            user_data: User registration data including name, email, password, and birth date
            
        Returns:
            Created user response with ID
            
        Raises:
            HTTPException: If email already exists or registration fails
        """
        try:
            return await self.controller.register_user(user_data)
        except ValueError as ve:
            logger.error(f"Validation error registering user: {ve}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error registering user: {str(e)}"
            )

    @router.get(
        "/get_all",
        response_model=List[UserResponse],
        status_code=status.HTTP_200_OK,
    )
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Get all active users with pagination.
        
        Args:
            skip: Number of users to skip (default: 0)
            limit: Maximum number of users to return (default: 100)
            
        Returns:
            List of user responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            return await self.controller.get_all_users(skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving users: {str(e)}"
            )

    @router.get(
        "/{user_id}",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_user(self, user_id: str) -> UserResponse:
        """
        Get a user by their ID.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            User response
            
        Raises:
            HTTPException: If user not found or retrieval fails
        """
        try:
            user = await self.controller.get_user(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found"
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving user: {str(e)}"
            )

    @router.get(
        "/email/{email}",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_user_by_email(self, email: str) -> UserResponse:
        """
        Get a user by their email address.
        
        Args:
            email: User email to search for
            
        Returns:
            User response
            
        Raises:
            HTTPException: If user not found or retrieval fails
        """
        try:
            user = await self.controller.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found"
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving user: {str(e)}"
            )

    @router.put(
        "/{user_id}",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK,
    )
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """
        Update user information.
        
        Args:
            user_id: User ID to update
            user_data: Fields to update (nome, email, data_nascimento)
            
        Returns:
            Updated user response
            
        Raises:
            HTTPException: If user not found, email exists, or update fails
        """
        try:
            user = await self.controller.update_user(user_id, user_data)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found"
                )
            return user
        except ValueError as ve:
            logger.error(f"Validation error updating user: {ve}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating user: {str(e)}"
            )

    @router.delete(
        "/{user_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_user(self, user_id: str) -> None:
        """Delete (deactivate) a user account.
        
        Args:
            user_id: User ID to delete
            
        Raises:
            HTTPException: If user not found or deletion fails
        """
        try:
            deleted = await self.controller.delete_user(user_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error deleting user: {str(e)}"
            )
