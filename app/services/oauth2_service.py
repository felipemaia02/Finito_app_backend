"""OAuth2 authentication service with JWT token generation and validation."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import bcrypt

from app.infrastructure.settings import get_settings
from app.infrastructure.logger import get_logger
from app.models.auth_schema import TokenData

logger = get_logger(__name__)


class OAuth2Service:
    """Service for OAuth2 token generation and validation."""

    def __init__(self):
        """Initialize the service with settings."""
        self.settings = get_settings()
        self.algorithm = "HS256"

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password
        """
        # Ensure password is a string and encode to bytes (bcrypt requirement)
        if isinstance(password, str):
            password = password.encode("utf-8")

        # Hash with bcrypt (rounds=12 is default)
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        try:
            # Ensure inputs are bytes (bcrypt requirement)
            if isinstance(plain_password, str):
                plain_password = plain_password.encode("utf-8")
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode("utf-8")

            return bcrypt.checkpw(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: Dictionary with token data (sub=email, etc)
            expires_delta: Token expiration time delta (uses default if None)

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        to_encode["type"] = "access"

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                hours=self.settings.jwt_access_token_expire_hours
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.algorithm
        )

        logger.debug(f"Access token created for subject: {data.get('sub')}")
        return encoded_jwt

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token.

        Args:
            data: Dictionary with token data (sub=email, etc)
            expires_delta: Token expiration time delta (uses default if None)

        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        to_encode["type"] = "refresh"

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default to configured refresh days
            expire = datetime.utcnow() + timedelta(
                days=self.settings.jwt_refresh_token_expire_days
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.algorithm
        )

        logger.debug(f"Refresh token created for subject: {data.get('sub')}")
        return encoded_jwt

    def create_token_pair(self, email: str, user_id: Optional[str] = None) -> Tuple[str, str, datetime]:
        """
        Create both access and refresh tokens.

        Args:
            email: User email
            user_id: User ID to embed in the token payload

        Returns:
            Tuple of (access_token, refresh_token, expires_at datetime)
        """
        payload: dict = {"sub": email}
        if user_id is not None:
            payload["user_id"] = user_id

        access_token_expires = timedelta(
            hours=self.settings.jwt_access_token_expire_hours
        )
        access_token = self.create_access_token(
            data=payload, expires_delta=access_token_expires
        )

        refresh_token = self.create_refresh_token(data=payload)

        expires_at = datetime.utcnow() + access_token_expires

        return access_token, refresh_token, expires_at

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        Validates token signature, expiration, and type.

        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")

        Returns:
            TokenData if valid, None if invalid or expired
        """
        try:
            payload = jwt.decode(
                token, self.settings.secret_key, algorithms=[self.algorithm]
            )

            sub: str = payload.get("sub")
            token_type_from_payload: str = payload.get("type", "access")
            exp: int = payload.get("exp")
            user_id: Optional[str] = payload.get("user_id")

            if sub is None:
                logger.warning("Token missing 'sub' claim")
                return None

            if exp is None:
                logger.warning("Token missing 'exp' claim")
                return None

            if token_type_from_payload != token_type:
                logger.warning(
                    f"Token type mismatch: expected {token_type}, got {token_type_from_payload}"
                )
                return None

            exp_datetime = datetime.utcfromtimestamp(exp)
            logger.debug(f"Token valid for subject: {sub}, expires at {exp_datetime}")

            token_data = TokenData(sub=sub, user_id=user_id, exp=exp, type=token_type_from_payload)
            logger.debug(
                f"Token verified for subject: {sub} (type: {token_type_from_payload})"
            )
            return token_data

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
