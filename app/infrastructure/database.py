"""
Asynchronous MongoDB database connection management.
Uses Motor for async operations with MongoDB.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.infrastructure.settings import get_settings
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class Database:
    """
    Manages asynchronous MongoDB connection lifecycle.
    Uses Motor for async operations and maintains global client/database instances.
    """

    _client: AsyncIOMotorClient = None
    _db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls) -> None:
        """
        Establish asynchronous connection to MongoDB.
        Should be called on application startup.
        """
        settings = get_settings()
        
        try:
            logger.info(f"Connecting to MongoDB: {settings.mongodb_db_name}")
            cls._client = AsyncIOMotorClient(settings.mongodb_url)
            cls._db = cls._client[settings.mongodb_db_name]
            
            await cls._client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {settings.mongodb_db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def disconnect(cls) -> None:
        """
        Close MongoDB connection.
        Should be called on application shutdown.
        """
        if cls._client is not None:
            logger.info("Disconnecting from MongoDB")
            cls._client.close()
            cls._db = None
            logger.info("Successfully disconnected from MongoDB")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """
        Get the active MongoDB database instance.
        
        Returns:
            AsyncIOMotorDatabase: The MongoDB database connection object
            
        Raises:
            RuntimeError: If database connection is not initialized
        """
        if cls._db is None:
            logger.error("Attempted to get database instance before initialization")
            raise RuntimeError("Database connection not initialized. Call Database.connect() first.")
        return cls._db

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """
        Get the active MongoDB client instance.
        
        Returns:
            AsyncIOMotorClient: The MongoDB client connection object
            
        Raises:
            RuntimeError: If database connection is not initialized
        """
        if cls._client is None:
            logger.error("Attempted to get client instance before initialization")
            raise RuntimeError("Database connection not initialized. Call Database.connect() first.")
        return cls._client

    @classmethod
    def is_connected(cls) -> bool:
        """
        Check if database connection is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return cls._client is not None and cls._db is not None
