from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from database import get_db
from models import Admin, Role
from schemas import (
    AdminCreate,
    AdminResponse,
    AdminUpdate,
    AdminUpdateRole,
    AdminListResponse,
    PaginatedResponse,
    ApiResponse
)
from auth_utils import get_password_hash, get_superadmin

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[AdminListResponse])
async def get_all_admins(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    username: Optional[str] = Query(None, description="Filter by username"),
    role_id: Optional[int] = Query(None, description="Filter by role ID"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Get list of all admins with pagination and filtering
    Superadmin only - requires superadmin role
    """
    query = db.query(Admin)

    # Apply filters
    if username:
        query = query.filter(Admin.username.ilike(f"%{username}%"))
    if role_id:
        query = query.filter(Admin.role_id == role_id)

    # Get total count before pagination
    total = query.count()

    # Order by created_at descending
    query = query.order_by(Admin.created_at.desc())

    # Calculate offset and apply pagination
    offset = (page - 1) * page_size
    admins = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return {
        "data": admins,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }

@router.get("/{admin_id}", response_model=ApiResponse[AdminResponse])
async def get_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Get single admin by ID
    Superadmin only - requires superadmin role
    """
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return {"data": admin}

@router.post("/", response_model=ApiResponse[AdminResponse], status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Create new admin user
    Superadmin only - requires superadmin role
    """
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

    return {"data": new_admin, "message": "Admin created successfully"}

@router.put("/{admin_id}", response_model=ApiResponse[AdminResponse])
async def update_admin(
    admin_id: int,
    admin_update: AdminUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Update admin user (username, password, or role)
    Superadmin only - requires superadmin role
    """
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    # Prevent superadmin from demoting themselves if they're the only superadmin
    if admin.id == current_admin.id and admin_update.role_id:
        # Check if current admin is superadmin
        if admin.role.slug == "superadmin":
            # Check if new role is not superadmin
            new_role = db.query(Role).filter(Role.id == admin_update.role_id).first()
            if new_role and new_role.slug != "superadmin":
                # Count superadmins
                superadmin_role = db.query(Role).filter(Role.slug == "superadmin").first()
                if superadmin_role:
                    superadmin_count = db.query(Admin).filter(Admin.role_id == superadmin_role.id).count()
                    if superadmin_count <= 1:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot demote the last superadmin. Promote another admin first."
                        )

    # Check if new username already exists (if username is being updated)
    if admin_update.username and admin_update.username != admin.username:
        existing_admin = db.query(Admin).filter(Admin.username == admin_update.username).first()
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        admin.username = admin_update.username

    # Update password if provided
    if admin_update.password:
        admin.hashed_password = get_password_hash(admin_update.password)

    # Update role if provided
    if admin_update.role_id:
        # Check if role exists
        new_role = db.query(Role).filter(Role.id == admin_update.role_id).first()
        if not new_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found"
            )
        admin.role_id = admin_update.role_id

    db.commit()
    db.refresh(admin)
    return {"data": admin, "message": "Admin updated successfully"}

@router.patch("/{admin_id}/role", response_model=ApiResponse[AdminResponse])
async def update_admin_role(
    admin_id: int,
    role_update: AdminUpdateRole,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Update only the role of an admin user
    Superadmin only - requires superadmin role
    """
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    # Check if new role exists
    new_role = db.query(Role).filter(Role.id == role_update.role_id).first()
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role not found"
        )

    # Prevent superadmin from demoting themselves if they're the only superadmin
    if admin.id == current_admin.id:
        if admin.role.slug == "superadmin" and new_role.slug != "superadmin":
            # Count superadmins
            superadmin_role = db.query(Role).filter(Role.slug == "superadmin").first()
            if superadmin_role:
                superadmin_count = db.query(Admin).filter(Admin.role_id == superadmin_role.id).count()
                if superadmin_count <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot demote the last superadmin. Promote another admin first."
                    )

    admin.role_id = role_update.role_id
    db.commit()
    db.refresh(admin)
    return {"data": admin, "message": "Admin role updated successfully"}

@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Delete admin user by ID
    Superadmin only - requires superadmin role
    """
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    # Prevent deletion of self
    if admin.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account"
        )

    # Prevent deletion of last superadmin
    if admin.role.slug == "superadmin":
        superadmin_role = db.query(Role).filter(Role.slug == "superadmin").first()
        if superadmin_role:
            superadmin_count = db.query(Admin).filter(Admin.role_id == superadmin_role.id).count()
            if superadmin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last superadmin"
                )

    db.delete(admin)
    db.commit()
    return None
