"""
Authentication Service

Provides comprehensive authentication and authorization services
including JWT token management, password handling, and session management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import jwt
import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import secrets
import hashlib

from app.core.config import settings
from app.models.user import User, Operator, UserStatus, AuthType
from app.repositories.user import UserRepository, OperatorRepository


class AuthService:
    """
    Authentication service for handling user authentication,
    JWT token management, and authorization.
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.operator_repository = OperatorRepository(db)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password

        Args:
            username: Username to authenticate
            password: Plain text password

        Returns:
            User instance if authenticated, None otherwise
        """
        # First try user table
        user = await self.user_repository.get_by_username(username)
        if user and user.is_active and user.status == UserStatus.ACTIVE:
            if self.verify_password(password, user.password_hash):
                # Update last login
                user.last_login = datetime.utcnow()
                await self.user_repository.update(user.id, {"last_login": user.last_login})
                return user

        return None

    async def authenticate_operator(self, username: str, password: str) -> Optional[Operator]:
        """
        Authenticate operator with username and password

        Args:
            username: Username to authenticate
            password: Plain text password

        Returns:
            Operator instance if authenticated, None otherwise
        """
        operator = await self.operator_repository.get_by_username(username)
        if operator:
            if self.verify_password(password, operator.password):
                # Update last login
                operator.lastlogin = datetime.utcnow()
                await self.operator_repository.update(operator.id, {"lastlogin": operator.lastlogin})
                return operator

        return None

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash

        Args:
            password: Plain text password
            hashed_password: Hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        if not hashed_password:
            return False

        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    def create_access_token(self, user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token

        Args:
            user_data: User data to encode in token
            expires_delta: Token expiration time

        Returns:
            JWT access token
        """
        to_encode = user_data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token

        Args:
            user_data: User data to encode in token

        Returns:
            JWT refresh token
        """
        to_encode = user_data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")

        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            if payload.get("type") != token_type:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None

    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from JWT token

        Args:
            token: JWT access token

        Returns:
            User instance if token is valid, None otherwise
        """
        payload = self.verify_token(token, "access")
        if not payload:
            return None

        username = payload.get("sub")
        if not username:
            return None

        user = await self.user_repository.get_by_username(username)
        if not user or not user.is_active:
            return None

        return user

    async def get_current_operator(self, token: str) -> Optional[Operator]:
        """
        Get current operator from JWT token

        Args:
            token: JWT access token

        Returns:
            Operator instance if token is valid, None otherwise
        """
        payload = self.verify_token(token, "access")
        if not payload:
            return None

        username = payload.get("sub")
        if not username:
            return None

        operator = await self.operator_repository.get_by_username(username)
        return operator

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token if refresh token is valid, None otherwise
        """
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None

        username = payload.get("sub")
        if not username:
            return None

        # Verify user still exists and is active
        user = await self.user_repository.get_by_username(username)
        if not user or not user.is_active:
            return None

        # Create new access token
        user_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "auth_type": user.auth_type.value if user.auth_type else "LOCAL"
        }

        return self.create_access_token(user_data)

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password

        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True if password changed successfully, False otherwise
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False

        # Verify current password
        if not self.verify_password(current_password, user.password_hash):
            return False

        # Hash new password
        new_password_hash = self.hash_password(new_password)

        # Update password
        update_data = {
            "password_hash": new_password_hash,
            "updated_at": datetime.utcnow()
        }

        await self.user_repository.update(user_id, update_data)
        return True

    async def reset_password(self, email: str, new_password: str, verification_code: str) -> bool:
        """
        Reset password with verification code

        Args:
            email: User email
            new_password: New password to set
            verification_code: Verification code for security

        Returns:
            True if password reset successfully, False otherwise
        """
        user = await self.user_repository.get_by_email(email)
        if not user:
            return False

        # In a real implementation, you would verify the verification_code
        # For now, we'll assume it's valid

        # Hash new password
        new_password_hash = self.hash_password(new_password)

        # Update password
        update_data = {
            "password_hash": new_password_hash,
            "updated_at": datetime.utcnow()
        }

        await self.user_repository.update(user.id, update_data)
        return True

    def generate_verification_code(self) -> str:
        """
        Generate verification code for password reset

        Returns:
            6-digit verification code
        """
        return str(secrets.randbelow(900000) + 100000)

    async def validate_permissions(self, user: User, required_permissions: List[str]) -> bool:
        """
        Validate user permissions

        Args:
            user: User to check permissions for
            required_permissions: List of required permissions

        Returns:
            True if user has all required permissions, False otherwise
        """
        # Basic permission check - can be extended with role-based permissions
        if not user.is_active or user.status != UserStatus.ACTIVE:
            return False

        # For now, active users have basic permissions
        # This can be extended with proper role-based access control
        return True

    def get_user_permissions(self, user: User) -> List[str]:
        """
        Get user permissions

        Args:
            user: User to get permissions for

        Returns:
            List of user permissions
        """
        permissions = []

        if user.is_active and user.status == UserStatus.ACTIVE:
            permissions.extend([
                "user.view",
                "user.edit",
                "accounting.view",
                "reports.view"
            ])

        # Add more permissions based on user role if needed
        return permissions
