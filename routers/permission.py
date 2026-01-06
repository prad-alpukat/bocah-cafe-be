"""
Permission router - Endpoints for managing permissions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from math import ceil
from database import get_db
from models import Permission, Admin
from schemas import PermissionResponse, PaginatedResponse, ApiResponse
from auth_utils import get_current_admin, require_permission

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PermissionResponse])
def get_all_permissions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    resource: Optional[str] = Query(None, description="Filter by resource (e.g., 'cafe', 'admin')"),
    search: Optional[str] = Query(None, description="Search by name or slug"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("permission:read"))
):
    """
    Get all permissions with pagination and filtering.
    Requires permission:read permission.
    """
    query = db.query(Permission)

    # Filter by resource
    if resource:
        query = query.filter(Permission.resource == resource)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Permission.name.ilike(search_term)) |
            (Permission.slug.ilike(search_term))
        )

    # Get total
    total = query.count()

    # Order and paginate
    query = query.order_by(Permission.resource, Permission.action)
    offset = (page - 1) * page_size
    permissions = query.offset(offset).limit(page_size).all()

    total_pages = ceil(total / page_size) if total > 0 else 0

    return {
        "data": permissions,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }


@router.get("/resources", response_model=List[str])
def get_available_resources(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("permission:read"))
):
    """
    Get list of available resource types.
    Requires permission:read permission.
    """
    resources = db.query(Permission.resource).distinct().order_by(Permission.resource).all()
    return [r[0] for r in resources]


@router.get("/grouped")
def get_permissions_grouped(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("permission:read"))
):
    """
    Get all permissions grouped by resource.
    Useful for displaying in UI.
    Requires permission:read permission.
    """
    permissions = db.query(Permission).order_by(Permission.resource, Permission.action).all()

    grouped = {}
    for perm in permissions:
        if perm.resource not in grouped:
            grouped[perm.resource] = []
        grouped[perm.resource].append(PermissionResponse.model_validate(perm))

    return {
        "data": grouped,
        "total": len(permissions)
    }


@router.get("/{permission_id}", response_model=ApiResponse[PermissionResponse])
def get_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("permission:read"))
):
    """
    Get single permission by ID.
    Requires permission:read permission.
    """
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return {"data": permission}


@router.get("/slug/{slug}", response_model=ApiResponse[PermissionResponse])
def get_permission_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_permission("permission:read"))
):
    """
    Get single permission by slug (e.g., 'cafe:create').
    Requires permission:read permission.
    """
    permission = db.query(Permission).filter(Permission.slug == slug).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return {"data": permission}
