from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Default credentials
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "743663")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "girish7890@A")

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    from app.services.mongodb_db import get_db
    
    db = await get_db()
    user = await db.find_one('users', {'email': email})
    
    if user is None:
        raise credentials_exception
    
    return user

def check_default_credentials(email: str, password: str) -> bool:
    """Check if credentials match default admin credentials"""
    # Handle the special case where user enters the default user ID
    if email == DEFAULT_USER_ID and password == DEFAULT_PASSWORD:
        return True
    return False

async def create_default_user_if_not_exists():
    """Create default admin user if it doesn't exist"""
    from app.services.mongodb_db import get_db
    
    db = await get_db()
    admin_user = await db.find_one('users', {'email': 'admin@inventory.com'})
    
    if not admin_user:
        # Create default admin user
        admin_user_data = {
            'username': 'admin',
            'email': 'admin@inventory.com',
            'password_hash': get_password_hash(DEFAULT_PASSWORD),
            'role': 'admin',
            'created_at': datetime.now().isoformat()
        }
        
        user_id = await db.insert_one('users', admin_user_data)
        print("✅ Created default admin user")
        return admin_user_data
    
    return None
