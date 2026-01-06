from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import Admin, Permission
from schemas import TokenData
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password with hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def authenticate_admin(db: Session, username: str, password: str):
    """Authenticate admin user"""
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated admin"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role_id: str = payload.get("role_id")
        role_slug: str = payload.get("role_slug")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role_id=role_id, role_slug=role_slug)
    except JWTError:
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.username == token_data.username).first()
    if admin is None:
        raise credentials_exception
    return admin

def require_role(required_role_slug: str):
    """
    Dependency factory to require a specific role slug
    Usage: @router.get("/", dependencies=[Depends(require_role("superadmin"))])
    """
    async def role_checker(current_admin: Admin = Depends(get_current_admin)):
        if current_admin.role.slug != required_role_slug:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role_slug}"
            )
        return current_admin
    return role_checker

async def get_superadmin(current_admin: Admin = Depends(get_current_admin)):
    """Dependency to require superadmin role"""
    if current_admin.role.slug != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Superadmin role required"
        )
    return current_admin

def has_role(admin: Admin, role_slug: str) -> bool:
    """Check if admin has a specific role by slug"""
    return admin.role.slug == role_slug

def is_superadmin(admin: Admin) -> bool:
    """Check if admin is a superadmin"""
    return admin.role.slug == "superadmin"

def has_role_id(admin: Admin, role_id: str) -> bool:
    """Check if admin has a specific role by ID"""
    return admin.role_id == role_id


# ============== Permission-based Access Control ==============

def get_admin_permissions(admin: Admin) -> List[str]:
    """
    Get list of permission slugs for an admin.
    Superadmin has all permissions by default.
    """
    if admin.role.slug == "superadmin":
        return ["*"]  # Superadmin has all permissions
    return [p.slug for p in admin.role.permissions]


def has_permission(admin: Admin, permission_slug: str) -> bool:
    """
    Check if admin has a specific permission.

    Args:
        admin: Admin object with role relationship loaded
        permission_slug: Permission slug like "cafe:create", "admin:delete"

    Returns:
        True if admin has the permission
    """
    # Superadmin always has all permissions
    if admin.role.slug == "superadmin":
        return True

    # Check if permission exists in role's permissions
    return any(p.slug == permission_slug for p in admin.role.permissions)


def has_any_permission(admin: Admin, permission_slugs: List[str]) -> bool:
    """Check if admin has ANY of the given permissions"""
    if admin.role.slug == "superadmin":
        return True

    admin_permissions = {p.slug for p in admin.role.permissions}
    return bool(admin_permissions & set(permission_slugs))


def has_all_permissions(admin: Admin, permission_slugs: List[str]) -> bool:
    """Check if admin has ALL of the given permissions"""
    if admin.role.slug == "superadmin":
        return True

    admin_permissions = {p.slug for p in admin.role.permissions}
    return set(permission_slugs).issubset(admin_permissions)


def require_permission(permission_slug: str):
    """
    Dependency factory to require a specific permission.

    Usage:
        @router.post("/", dependencies=[Depends(require_permission("cafe:create"))])
        def create_cafe(...):
            ...

    Or as parameter:
        @router.post("/")
        def create_cafe(current_admin: Admin = Depends(require_permission("cafe:create"))):
            ...
    """
    async def permission_checker(current_admin: Admin = Depends(get_current_admin)):
        if not has_permission(current_admin, permission_slug):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {permission_slug}"
            )
        return current_admin
    return permission_checker


def require_any_permission(*permission_slugs: str):
    """
    Dependency factory to require ANY of the specified permissions.

    Usage:
        @router.get("/", dependencies=[Depends(require_any_permission("cafe:read", "cafe:manage"))])
    """
    async def permission_checker(current_admin: Admin = Depends(get_current_admin)):
        if not has_any_permission(current_admin, list(permission_slugs)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required one of: {', '.join(permission_slugs)}"
            )
        return current_admin
    return permission_checker


def require_all_permissions(*permission_slugs: str):
    """
    Dependency factory to require ALL of the specified permissions.

    Usage:
        @router.delete("/", dependencies=[Depends(require_all_permissions("cafe:delete", "cafe:manage"))])
    """
    async def permission_checker(current_admin: Admin = Depends(get_current_admin)):
        if not has_all_permissions(current_admin, list(permission_slugs)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required all: {', '.join(permission_slugs)}"
            )
        return current_admin
    return permission_checker
