"""Group routes with class-based views using fastapi-utils."""

from typing import List
from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi_utils.cbv import cbv

from app.controllers.group_controller import GroupController
from app.infrastructure.dependencies.group_dependencies import GroupDependencies
from app.infrastructure.dependencies.oauth2_dependencies import verify_oauth2_token
from app.infrastructure.dependencies.auth_dependencies import verify_api_key
from app.models.group_schema import GroupCreate, GroupUpdate, GroupResponse, AddUserRequest
from app.models.auth_schema import TokenData
from app.models.response_schema import StandardResponse
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["groups"])


@cbv(router)
class GroupViews:
    """Class-based views for group operations."""

    controller: GroupController = Depends(GroupDependencies.get_controller)
    current_user: TokenData = Security(verify_oauth2_token)
    api_key: str = Security(verify_api_key)

    @router.post(
        "/groups",
        response_model=StandardResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_group(self, group_data: GroupCreate) -> StandardResponse:
        """Create a new group."""
        try:
            await self.controller.create_group(group_data, self.current_user.sub)
            return StandardResponse(message="Group created successfully")
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating group: {str(e)}",
            )

    @router.get("/groups/me", response_model=List[GroupResponse])
    async def get_my_groups(self) -> List[GroupResponse]:
        """Get all groups the authenticated user belongs to."""
        try:
            return await self.controller.get_groups_by_user_email(self.current_user.sub)
        except Exception as e:
            logger.error(f"Error fetching groups for user {self.current_user.sub}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error fetching user groups: {str(e)}",
            )

    @router.get("/groups/{group_id}", response_model=GroupResponse)
    async def get_group(self, group_id: str) -> GroupResponse:
        """Get a group by ID (user must be a member)."""
        try:
            group = await self.controller.get_group_by_id(group_id, self.current_user.sub)
            if group is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Group {group_id} not found",
                )
            return group
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error fetching group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error fetching group: {str(e)}",
            )

    @router.patch("/groups/{group_id}", response_model=StandardResponse)
    async def update_group(self, group_id: str, group_data: GroupUpdate) -> StandardResponse:
        """Update a group's name (only if the authenticated user is a member)."""
        try:
            result = await self.controller.update_group(group_id, group_data, self.current_user.sub)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Group {group_id} not found",
                )
            return StandardResponse(message="Group updated successfully")
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error updating group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating group: {str(e)}",
            )

    @router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_group(self, group_id: str) -> None:
        """Delete a group (only if the authenticated user is the creator)."""
        try:
            deleted = await self.controller.delete_group(group_id, self.current_user.sub)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Group {group_id} not found",
                )
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except Exception as e:
            logger.error(f"Error deleting group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error deleting group: {str(e)}",
            )

    @router.post(
        "/groups/{group_id}/users",
        response_model=StandardResponse,
    )
    async def add_user_to_group(
        self, group_id: str, body: AddUserRequest
    ) -> StandardResponse:
        """Add a user to a group (only if the authenticated user is a member)."""
        try:
            result = await self.controller.add_user_to_group(group_id, body.user_id, self.current_user.sub)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Group {group_id} not found",
                )
            return StandardResponse(message="User added to group successfully")
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error adding user to group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error adding user to group: {str(e)}",
            )

    @router.delete(
        "/groups/{group_id}/users/{user_id}",
        response_model=StandardResponse,
    )
    async def remove_user_from_group(
        self, group_id: str, user_id: str
    ) -> StandardResponse:
        """Remove a user from a group (only if the authenticated user is a member)."""
        try:
            result = await self.controller.remove_user_from_group(group_id, user_id, self.current_user.sub)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Group {group_id} not found",
                )
            return StandardResponse(message="User removed from group successfully")
        except HTTPException:
            raise
        except PermissionError as pe:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
            )
        except Exception as e:
            logger.error(f"Error removing user from group {group_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error removing user from group: {str(e)}",
            )
