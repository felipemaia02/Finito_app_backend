"""Public user routes (no authentication required)."""

from fastapi import APIRouter, Depends, HTTPException, Security, status

from fastapi_utils.cbv import cbv

from app.controllers.user_controller import UserController
from app.infrastructure.dependencies.user_dependencies import UserDependencies
from app.infrastructure.dependencies.auth_dependencies import verify_api_key
from app.models.user_schema import UserCreate, UserResponse
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(tags=["users"], prefix="/users")


@cbv(router)
class UserPublicViews:
    """Public user endpoints (no authentication required)."""

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
