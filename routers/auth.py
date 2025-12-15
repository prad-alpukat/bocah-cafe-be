from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import Admin
from schemas import AdminCreate, AdminResponse, Token, LoginRequest
from auth_utils import get_password_hash, authenticate_admin, create_access_token, get_current_admin
from config import settings

router = APIRouter()

@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    """
    Register new admin user
    """
    # Check if username already exists
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new admin
    hashed_password = get_password_hash(admin.password)
    new_admin = Admin(
        username=admin.username,
        hashed_password=hashed_password
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return new_admin

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login admin and get access token
    """
    admin = authenticate_admin(db, login_data.username, login_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    """
    Get current admin information
    """
    return current_admin
