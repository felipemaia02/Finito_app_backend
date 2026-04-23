"""Protected user routes (OAuth2 token required)."""

from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi_utils.cbv import cbv
from typing import List

from app.controllers.user_controller import UserController
from app.infrastructure.dependencies.user_dependencies import UserDependencies
from app.infrastructure.dependencies.oauth2_dependencies import verify_oauth2_token
from app.infrastructure.dependencies.auth_dependencies import verify_api_key
from app.models.user_schema import UserUpdate, UserResponse, UserPublicInfo
from app.models.auth_schema import TokenData
from app.models.response_schema import StandardResponse
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(tags=["users"], prefix="/users")


@cbv(router)
class UserPrivateViews:
    """Protected user endpoints (OAuth2 token required)."""

    controller: UserController = Depends(UserDependencies.get_controller)
    current_user: TokenData = Security(verify_oauth2_token)
    api_key: str = Security(verify_api_key)

    @router.get(
        "/",
        response_model=List[UserResponse],
        status_code=status.HTTP_200_OK,
    )
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """List all users with pagination."""
        try:
            return await self.controller.get_all_users(skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error listing users: {str(e)}",
            )

    @router.get(
        "/email/{email}",
        response_model=UserPublicInfo,
        status_code=status.HTTP_200_OK,
    )
    async def get_user_by_email(self, email: str) -> UserPublicInfo:
        """Get a user's ID and email by their email address."""
        try:
            user = await self.controller.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found",
                )
            return UserPublicInfo(id=user.id, email=user.email)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving user: {str(e)}",
            )

    @router.get(
        "/me",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_me(self) -> UserResponse:
        """Get the authenticated user's data."""
        try:
            user = await self.controller.get_user(self.current_user.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving user: {str(e)}",
            )

    @router.put(
        "/me",
        response_model=StandardResponse,
        status_code=status.HTTP_200_OK,
    )
    async def update_me(self, user_data: UserUpdate) -> StandardResponse:
        """Update the authenticated user's information."""
        try:
            updated = await self.controller.update_user(self.current_user.user_id, user_data)
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return StandardResponse(message="User updated successfully")
        except ValueError as ve:
            logger.error(f"Validation error updating user: {ve}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating user: {str(e)}",
            )

    @router.delete(
        "/me",
        response_model=StandardResponse,
        status_code=status.HTTP_200_OK,
    )
    async def delete_me(self) -> StandardResponse:
        """Delete (deactivate) the authenticated user's account."""
        try:
            deleted = await self.controller.delete_user(self.current_user.user_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return StandardResponse(message="User deleted successfully")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error deleting user: {str(e)}",
            )

    @router.get(
        "/{user_id}",
        response_model=UserResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Get a user by their ID."""
        try:
            user = await self.controller.get_user(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found",
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error retrieving user: {str(e)}",
            )

    @router.put(
        "/{user_id}",
        response_model=StandardResponse,
        status_code=status.HTTP_200_OK,
    )
    async def update_user_by_id(self, user_id: str, user_data: UserUpdate) -> StandardResponse:
        """Update a user by their ID."""
        try:
            updated = await self.controller.update_user(user_id, user_data)
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found",
                )
            return StandardResponse(message="User updated successfully")
        except ValueError as ve:
            logger.error(f"Validation error updating user {user_id}: {ve}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating user: {str(e)}",
            )

    @router.delete(
        "/{user_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_user_by_id(self, user_id: str) -> None:
        """Delete a user by their ID."""
        try:
            deleted = await self.controller.delete_user(user_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found",
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error deleting user: {str(e)}",
            )
