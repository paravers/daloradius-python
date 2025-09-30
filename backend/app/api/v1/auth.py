"""
Authentication API Routes

Comprehensive authentication endpoints including login, logout, registration,
password management, and token operations.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db
from app.core.config import settings
from app.services.auth import AuthService
from app.models.user import User, UserStatus, AuthType
from app.repositories.user import UserRepository


router = APIRouter()
security = HTTPBearer()


# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=256)
    first_name: Optional[str] = Field(None, max_length=200)
    last_name: Optional[str] = Field(None, max_length=200)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=256)
    new_password: str = Field(..., min_length=6, max_length=256)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=256)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    status: str
    auth_type: str
    last_login: Optional[datetime]
    created_at: datetime
    permissions: List[str] = []


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login authentication

    Authenticates user credentials and returns JWT tokens
    """
    auth_service = AuthService(db)

    # Try to authenticate user first, then operator
    user = await auth_service.authenticate_user(login_data.username, login_data.password)

    if not user:
        # Try operator authentication
        operator = await auth_service.authenticate_operator(login_data.username, login_data.password)
        if not operator:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert operator to user-like structure for token
        user_data = {
            "sub": operator.username,
            "user_id": operator.id,
            "email": operator.username,  # Operators might not have email
            "auth_type": "OPERATOR",
            "user_type": "operator"
        }
    else:
        user_data = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "auth_type": user.auth_type.value if user.auth_type else "LOCAL",
            "user_type": "user"
        }

    # Generate tokens
    access_token = auth_service.create_access_token(user_data)
    refresh_token = auth_service.create_refresh_token(user_data)

    # Get user permissions
    if user:
        permissions = auth_service.get_user_permissions(user)
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "status": user.status.value if user.status else "ACTIVE",
            "auth_type": user.auth_type.value if user.auth_type else "LOCAL",
            "last_login": user.last_login,
            "permissions": permissions
        }
    else:
        # Operator info
        user_info = {
            "id": operator.id,
            "username": operator.username,
            "email": operator.username,
            "first_name": operator.firstname,
            "last_name": operator.lastname,
            "is_active": True,
            "status": "ACTIVE",
            "auth_type": "OPERATOR",
            "last_login": operator.lastlogin,
            "permissions": ["operator.view", "operator.manage"]
        }

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_info
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User logout

    Invalidates the current session (in a full implementation,
    you would add token to a blacklist)
    """
    # In a production environment, you would:
    # 1. Add token to blacklist
    # 2. Log the logout event
    # 3. Clear any server-side sessions

    return {"message": "Successfully logged out"}


@router.post("/register", response_model=LoginResponse)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    User registration

    Creates new user account and returns authentication tokens
    """
    auth_service = AuthService(db)
    user_repo = UserRepository(db)

    # Check if username already exists
    existing_user = await user_repo.get_by_username(register_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = await user_repo.get_by_email(register_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    password_hash = auth_service.hash_password(register_data.password)

    user_data = {
        "username": register_data.username,
        "email": register_data.email,
        "password_hash": password_hash,
        "first_name": register_data.first_name,
        "last_name": register_data.last_name,
        "auth_type": AuthType.LOCAL,
        "is_active": True,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.utcnow()
    }

    user = await user_repo.create(user_data)

    # Generate tokens
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "email": user.email,
        "auth_type": "LOCAL"
    }

    access_token = auth_service.create_access_token(token_data)
    refresh_token = auth_service.create_refresh_token(token_data)

    # Get user permissions
    permissions = auth_service.get_user_permissions(user)

    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "status": user.status.value if user.status else "ACTIVE",
        "auth_type": user.auth_type.value if user.auth_type else "LOCAL",
        "last_login": user.last_login,
        "permissions": permissions
    }

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_info
    )


@router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token

    Creates new access token from valid refresh token
    """
    auth_service = AuthService(db)

    new_access_token = await auth_service.refresh_access_token(refresh_data.refresh_token)

    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information

    Returns detailed information about the authenticated user
    """
    auth_service = AuthService(db)
    permissions = auth_service.get_user_permissions(current_user)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        status=current_user.status.value if current_user.status else "ACTIVE",
        auth_type=current_user.auth_type.value if current_user.auth_type else "LOCAL",
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        permissions=permissions
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password

    Changes the password for the authenticated user
    """
    auth_service = AuthService(db)

    success = await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate password reset

    Sends verification code to user's email (in production)
    """
    auth_service = AuthService(db)
    user_repo = UserRepository(db)

    user = await user_repo.get_by_email(forgot_data.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a verification code has been sent"}

    # Generate verification code
    verification_code = auth_service.generate_verification_code()

    # In production, you would:
    # 1. Store the verification code in database with expiration
    # 2. Send email with verification code
    # For now, we'll just log it (don't do this in production!)
    print(f"Verification code for {forgot_data.email}: {verification_code}")

    return {"message": "If the email exists, a verification code has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with verification code

    Resets user password using verification code
    """
    auth_service = AuthService(db)

    # In production, you would verify the verification code against stored value
    # For now, we'll accept any 6-digit code
    if len(reset_data.verification_code) != 6 or not reset_data.verification_code.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    success = await auth_service.reset_password(
        reset_data.email,
        reset_data.new_password,
        reset_data.verification_code
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or verification code"
        )

    return {"message": "Password reset successfully"}


@router.post("/validate-token")
async def validate_token(
    current_user: User = Depends(get_current_user)
):
    """
    Validate authentication token

    Checks if the provided token is valid
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }
