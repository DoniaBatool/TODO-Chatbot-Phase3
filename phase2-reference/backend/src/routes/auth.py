"""Authentication API endpoints (signup, login, protected)."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.auth.dependencies import get_current_user
from src.auth.jwt import create_jwt_token, get_token_expiry_seconds
from src.auth.password import hash_password, verify_password
from src.db import get_session
from src.models import User
from src.schemas import LoginRequest, LoginResponse, SignupRequest, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/auth/signup", response_model=UserResponse, status_code=201)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user account.
    
    Args:
        signup_data: User registration data (email, password, name)
        session: Database session
    
    Returns:
        UserResponse: Created user data (no password)
    
    Raises:
        HTTPException: 400 if email already exists
    """
    # Convert email to lowercase for case-insensitive matching
    email_lower = signup_data.email.lower()
    
    # Check if email already exists
    statement = select(User).where(User.email == email_lower)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Generate UUID for new user
        user_id = str(uuid.uuid4())
        
        # Hash password before storing
        password_hashed = hash_password(signup_data.password)
        
        # Create new user
        user = User(
            id=user_id,
            email=email_lower,
            name=signup_data.name,
            password_hash=password_hashed
        )
        
        # Save to database
        session.add(user)
        session.commit()
        session.refresh(user)
        
        logger.info("User signup success: email=%s id=%s", email_lower, user_id)
        # Return user data (password_hash excluded by UserResponse schema)
        return user
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        ) from e


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return JWT token.
    
    Args:
        login_data: User login credentials (email, password)
        session: Database session
    
    Returns:
        LoginResponse: JWT token and user data
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Convert email to lowercase
    email_lower = login_data.email.lower()
    
    # Look up user by email
    statement = select(User).where(User.email == email_lower)
    user = session.exec(statement).first()
    
    # Check if user exists
    if not user:
        logger.warning("Login failed: email not found (%s)", email_lower)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user has password (required for email/password login)
    if not user.password_hash:
        logger.warning("Login failed: user has no password_hash (%s)", email_lower)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        logger.warning("Login failed: invalid password (%s)", email_lower)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Password is correct - generate JWT token
    try:
        access_token = create_jwt_token(user.id, user.email)
        
        logger.info("Login success: email=%s id=%s", user.email, user.id)
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=get_token_expiry_seconds(),
            user=UserResponse.model_validate(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate token: {str(e)}"
        ) from e


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get authenticated user information from JWT token.
    
    This is a protected endpoint that requires valid JWT token.
    
    Args:
        user_id: Authenticated user ID from JWT token (injected by middleware)
        session: Database session
    
    Returns:
        UserResponse: Current user data
    
    Raises:
        HTTPException: 401 if token invalid, 404 if user not found
    """
    # Get user from database
    user = session.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

