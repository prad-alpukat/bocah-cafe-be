from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import Admin, Role, Permission
from schemas import AdminCreate, AdminResponse, Token, LoginRequest, ApiResponse, MyPermissionsResponse, PermissionResponse
from auth_utils import get_password_hash, authenticate_admin, create_access_token, get_current_admin
from config import settings

router = APIRouter()

@router.post("/register", response_model=ApiResponse[AdminResponse], status_code=status.HTTP_201_CREATED)
def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    """
    Register new admin user
    Note: This endpoint can be disabled via ALLOW_ADMIN_REGISTRATION environment variable
    """
    # Check if registration is allowed
    if not settings.ALLOW_ADMIN_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin registration is currently disabled"
        )

    # Check if username already exists
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if role_id exists
    role = db.query(Role).filter(Role.id == admin.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role not found"
        )

    # Create new admin
    hashed_password = get_password_hash(admin.password)
    new_admin = Admin(
        username=admin.username,
        hashed_password=hashed_password,
        role_id=admin.role_id
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"data": new_admin, "message": "Admin registered successfully"}

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
        data={"sub": admin.username, "role_id": admin.role_id, "role_slug": admin.role.slug},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=ApiResponse[AdminResponse])
def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    """
    Get current admin information
    """
    return {"data": current_admin}


@router.get("/me/permissions", response_model=ApiResponse[MyPermissionsResponse])
def get_current_admin_permissions(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get current admin's role and permissions.
    No special permission required - users can always view their own permissions.

    Returns:
        - role: Basic role information (id, name, slug)
        - is_superadmin: True if superadmin (has all permissions by default)
        - permissions: List of assigned permissions (empty for superadmin since they have all)
    """
    is_superadmin = current_admin.role.slug == "superadmin"

    if is_superadmin:
        # Superadmin has all permissions - return all permissions from database
        all_permissions = db.query(Permission).order_by(Permission.resource, Permission.action).all()
        permissions = [PermissionResponse.model_validate(p) for p in all_permissions]
    else:
        # Regular user - return assigned permissions
        permissions = [PermissionResponse.model_validate(p) for p in current_admin.role.permissions]

    return {
        "data": {
            "role": {
                "id": current_admin.role.id,
                "name": current_admin.role.name,
                "slug": current_admin.role.slug
            },
            "is_superadmin": is_superadmin,
            "permissions": permissions
        },
        "message": "Success"
    }
