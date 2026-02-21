"""Create User use case."""
from app.domain.interfaces.user_repository_interface import IUserRepository
from app.domain.entities.user_entity import User
from app.models.user_schema import UserCreate, UserResponse
from app.infrastructure.logger import get_logger
from app.domain.interfaces.use_case import IUseCase
from app.use_cases.user.password_utils import hash_password

logger = get_logger(__name__)


class CreateUserUseCase(IUseCase[UserCreate, UserResponse]):
    """Use case for creating a new user and registering them in the system."""
    
    def __init__(self, repository: IUserRepository):
        """
        Initialize the use case with a repository dependency.
        
        Args:
            repository: Implementation of IUserRepository
        """
        self.repository = repository
    
    async def execute(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user with encrypted password.
        
        Args:
            user_data: UserCreate schema with user details
            
        Returns:
            UserResponse with the created user
            
        Raises:
            ValueError: If email already exists
            Exception: If database operation fails
        """
        try:
            logger.info(f"Creating user with email: {user_data.email}")
            
            existing_user = await self.repository.get_by_email(user_data.email)
            if existing_user:
                logger.warning(f"User with email {user_data.email} already exists")
                raise ValueError(f"Email {user_data.email} is already registered")
            
            hashed_password = hash_password(user_data.password)
            
            user = User(
                name=user_data.name,
                email=user_data.email.lower(),
                password=hashed_password,
                date_birth=user_data.date_birth,
                is_active=True
            )

            created_user = await self.repository.create(user)
            
            logger.info(f"User created successfully with ID: {created_user.id} and email: {created_user.email}")
            return UserResponse(**created_user.model_dump())
        except ValueError as ve:
            logger.warning(f"Validation error creating user: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
