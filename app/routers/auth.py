from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import timedelta
from app.models.user import User, UserCreate, UserLogin, Token
from app.utils.auth import (
    verify_password, 
    create_access_token, 
    get_current_user,
    check_default_credentials,
    create_default_user_if_not_exists,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.services.mongodb_db import get_db
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return access token"""
    db = await get_db()
    
    # Check default credentials first
    if check_default_credentials(user_credentials.email, user_credentials.password):
        # Create default user if doesn't exist
        await create_default_user_if_not_exists()
        user_email = 'admin@inventory.com'
    else:
        user_email = user_credentials.email
    
    # Get user from database
    user_record = await db.find_one('users', {'email': user_email})
    
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user_record['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_record['email']}, 
        expires_delta=access_token_expires
    )
    
    # Return user data without password
    user_response = {
        'id': user_record['id'],
        'username': user_record['username'],
        'email': user_record['email'],
        'role': user_record['role'],
        'created_at': user_record['created_at']
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register a new user"""
    db = await get_db()
    
    # Check if user already exists
    existing_user = await db.find_one('users', {'email': user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await db.find_one('users', {'username': user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    from app.utils.auth import get_password_hash
    
    new_user = {
        'username': user.username,
        'email': user.email,
        'password_hash': get_password_hash(user.password),
        'role': user.role,
        'created_at': datetime.now().isoformat()
    }
    
    user_id = await db.insert_one('users', new_user)
    new_user['id'] = user_id
    
    # Return user without password
    user_response = {
        'id': new_user['id'],
        'username': new_user['username'],
        'email': new_user['email'],
        'role': new_user['role'],
        'created_at': new_user['created_at']
    }
    
    return user_response

@router.get("/verify", response_model=User)
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify JWT token and return current user"""
    return {
        'id': current_user['id'],
        'username': current_user['username'],
        'email': current_user['email'],
        'role': current_user['role'],
        'created_at': current_user['created_at']
    }

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        'id': current_user['id'],
        'username': current_user['username'],
        'email': current_user['email'],
        'role': current_user['role'],
        'created_at': current_user['created_at']
    }
