from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from math import ceil
from database import get_db
from models import Role, Admin, Permission
from schemas import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissionsResponse,
    RolePermissionsUpdate,
    RolePermissionsSlugsUpdate,
    PermissionResponse,
    PaginatedResponse,
    ApiResponse
)
from auth_utils import get_superadmin, require_permission

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[RoleResponse])
async def get_all_roles(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    name: Optional[str] = Query(None, description="Filter by role name"),
    slug: Optional[str] = Query(None, description="Filter by role slug"),
    include_system: bool = Query(True, description="Include system roles in results"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Get list of all roles with pagination and filtering
    Superadmin only - requires superadmin role
    """
    query = db.query(Role)

    # Apply filters
    if name:
        query = query.filter(Role.name.ilike(f"%{name}%"))
    if slug:
        query = query.filter(Role.slug.ilike(f"%{slug}%"))
    if not include_system:
        query = query.filter(Role.is_system_role == False)

    # Get total count before pagination
    total = query.count()

    # Order by created_at descending
    query = query.order_by(Role.created_at.desc())

    # Calculate offset and apply pagination
    offset = (page - 1) * page_size
    roles = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return {
        "data": roles,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }

@router.get("/{role_id}", response_model=ApiResponse[RoleResponse])
async def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Get single role by ID
    Superadmin only - requires superadmin role
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return {"data": role}

@router.post("/", response_model=ApiResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Create new role
    Superadmin only - requires superadmin role
    """
    # Check if role name already exists
    db_role = db.query(Role).filter(Role.name == role.name).first()
    if db_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )

    # Check if slug already exists
    db_role = db.query(Role).filter(Role.slug == role.slug).first()
    if db_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role slug already exists"
        )

    # Create new role
    new_role = Role(
        name=role.name,
        slug=role.slug,
        description=role.description,
        is_system_role=False  # User-created roles are not system roles
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return {"data": new_role, "message": "Role created successfully"}

@router.put("/{role_id}", response_model=ApiResponse[RoleResponse])
async def update_role(
    role_id: str,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Update role
    Superadmin only - requires superadmin role
    Note: System roles cannot be updated
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Prevent updating system roles
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update system roles"
        )

    # Check if new name already exists (if name is being updated)
    if role_update.name and role_update.name != role.name:
        existing_role = db.query(Role).filter(Role.name == role_update.name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists"
            )
        role.name = role_update.name

    # Check if new slug already exists (if slug is being updated)
    if role_update.slug and role_update.slug != role.slug:
        existing_role = db.query(Role).filter(Role.slug == role_update.slug).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role slug already exists"
            )
        role.slug = role_update.slug

    # Update description if provided
    if role_update.description is not None:
        role.description = role_update.description

    db.commit()
    db.refresh(role)
    return {"data": role, "message": "Role updated successfully"}

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Delete role by ID
    Superadmin only - requires superadmin role
    Note: System roles and roles assigned to admins cannot be deleted
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Prevent deletion of system roles
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system roles"
        )

    # Check if any admin is using this role
    admin_count = db.query(Admin).filter(Admin.role_id == role_id).count()
    if admin_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role. {admin_count} admin(s) are currently assigned to this role"
        )

    db.delete(role)
    db.commit()
    return None

@router.get("/slug/{slug}", response_model=ApiResponse[RoleResponse])
async def get_role_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_superadmin)
):
    """
    Get role by slug
    Superadmin only - requires superadmin role
    """
    role = db.query(Role).filter(Role.slug == slug).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return {"data": role}


# ============== Permission Management Endpoints ==============

@router.get("/{role_id}/permissions", response_model=ApiResponse[RoleWithPermissionsResponse])
async def get_role_permissions(
    role_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("role:manage_permissions"))
):
    """
    Get role with all its permissions.
    Requires role:manage_permissions permission.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return {"data": role}


@router.put("/{role_id}/permissions", response_model=ApiResponse[RoleWithPermissionsResponse])
async def update_role_permissions(
    role_id: str,
    permission_update: RolePermissionsUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("role:manage_permissions"))
):
    """
    Replace all permissions for a role.
    Requires role:manage_permissions permission.

    Note: Superadmin role permissions cannot be modified (they have all permissions by default).
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Prevent modifying superadmin permissions
    if role.slug == "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify superadmin permissions. Superadmin has all permissions by default."
        )

    # Get permissions by IDs
    permissions = db.query(Permission).filter(
        Permission.id.in_(permission_update.permission_ids)
    ).all()

    if len(permissions) != len(permission_update.permission_ids):
        found_ids = {p.id for p in permissions}
        missing_ids = set(permission_update.permission_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Some permissions not found: {list(missing_ids)}"
        )

    # Replace permissions
    role.permissions = permissions
    db.commit()
    db.refresh(role)

    return {
        "data": role,
        "message": f"Updated permissions for role '{role.name}'. Total: {len(permissions)} permissions."
    }


@router.put("/{role_id}/permissions/slugs", response_model=ApiResponse[RoleWithPermissionsResponse])
async def update_role_permissions_by_slugs(
    role_id: str,
    permission_update: RolePermissionsSlugsUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("role:manage_permissions"))
):
    """
    Replace all permissions for a role using permission slugs.
    Requires role:manage_permissions permission.

    Example request body:
    {
        "permission_slugs": ["cafe:create", "cafe:update", "cafe:read"]
    }
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Prevent modifying superadmin permissions
    if role.slug == "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify superadmin permissions. Superadmin has all permissions by default."
        )

    # Get permissions by slugs
    permissions = db.query(Permission).filter(
        Permission.slug.in_(permission_update.permission_slugs)
    ).all()

    if len(permissions) != len(permission_update.permission_slugs):
        found_slugs = {p.slug for p in permissions}
        missing_slugs = set(permission_update.permission_slugs) - found_slugs
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Some permissions not found: {list(missing_slugs)}"
        )

    # Replace permissions
    role.permissions = permissions
    db.commit()
    db.refresh(role)

    return {
        "data": role,
        "message": f"Updated permissions for role '{role.name}'. Total: {len(permissions)} permissions."
    }


@router.post("/{role_id}/permissions/add", response_model=ApiResponse[RoleWithPermissionsResponse])
async def add_permissions_to_role(
    role_id: str,
    permission_update: RolePermissionsSlugsUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("role:manage_permissions"))
):
    """
    Add permissions to a role (without removing existing ones).
    Requires role:manage_permissions permission.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    if role.slug == "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify superadmin permissions."
        )

    # Get permissions to add
    permissions_to_add = db.query(Permission).filter(
        Permission.slug.in_(permission_update.permission_slugs)
    ).all()

    if len(permissions_to_add) != len(permission_update.permission_slugs):
        found_slugs = {p.slug for p in permissions_to_add}
        missing_slugs = set(permission_update.permission_slugs) - found_slugs
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Some permissions not found: {list(missing_slugs)}"
        )

    # Add only new permissions
    current_slugs = {p.slug for p in role.permissions}
    added_count = 0
    for perm in permissions_to_add:
        if perm.slug not in current_slugs:
            role.permissions.append(perm)
            added_count += 1

    db.commit()
    db.refresh(role)

    return {
        "data": role,
        "message": f"Added {added_count} new permission(s) to role '{role.name}'."
    }


@router.post("/{role_id}/permissions/remove", response_model=ApiResponse[RoleWithPermissionsResponse])
async def remove_permissions_from_role(
    role_id: str,
    permission_update: RolePermissionsSlugsUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("role:manage_permissions"))
):
    """
    Remove specific permissions from a role.
    Requires role:manage_permissions permission.
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    if role.slug == "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify superadmin permissions."
        )

    # Remove permissions
    slugs_to_remove = set(permission_update.permission_slugs)
    removed_count = 0
    role.permissions = [p for p in role.permissions if p.slug not in slugs_to_remove]

    # Count how many were actually removed
    removed_count = len(slugs_to_remove)

    db.commit()
    db.refresh(role)

    return {
        "data": role,
        "message": f"Removed permission(s) from role '{role.name}'."
    }
