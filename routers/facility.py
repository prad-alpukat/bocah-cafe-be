from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from database import get_db
from models import Facility, Admin
from schemas import FacilityCreate, FacilityUpdate, FacilityResponse, PaginatedResponse, ApiResponse
from auth_utils import get_current_admin

router = APIRouter()

# Public endpoint - List all facilities
@router.get("/", response_model=PaginatedResponse[FacilityResponse])
def get_all_facilities(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search by facility name"),
    db: Session = Depends(get_db)
):
    """
    Get list of all available facilities with pagination
    Public endpoint - no authentication required
    """
    query = db.query(Facility)

    # Apply search filter
    if search:
        query = query.filter(Facility.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Order and paginate
    query = query.order_by(Facility.name)
    offset = (page - 1) * page_size
    facilities = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return {
        "data": facilities,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }

# Public endpoint - Get single facility by ID
@router.get("/{facility_id}", response_model=ApiResponse[FacilityResponse])
def get_facility(facility_id: str, db: Session = Depends(get_db)):
    """
    Get single facility by ID
    Public endpoint - no authentication required
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if facility is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    return {"data": facility}

# Admin only endpoints - Require authentication
@router.post("/", response_model=ApiResponse[FacilityResponse], status_code=status.HTTP_201_CREATED)
def create_facility(
    facility: FacilityCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create new facility
    Admin only - requires authentication
    """
    # Check if facility with same name or slug already exists
    existing = db.query(Facility).filter(
        (Facility.name == facility.name) | (Facility.slug == facility.slug)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility with this name or slug already exists"
        )

    new_facility = Facility(**facility.model_dump())
    db.add(new_facility)
    db.commit()
    db.refresh(new_facility)
    return {"data": new_facility, "message": "Facility created successfully"}

@router.put("/{facility_id}", response_model=ApiResponse[FacilityResponse])
def update_facility(
    facility_id: str,
    facility_update: FacilityUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update facility by ID
    Admin only - requires authentication
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if facility is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    update_data = facility_update.model_dump(exclude_unset=True)

    # Check for duplicate name or slug
    if 'name' in update_data or 'slug' in update_data:
        name_check = update_data.get('name', facility.name)
        slug_check = update_data.get('slug', facility.slug)
        existing = db.query(Facility).filter(
            Facility.id != facility_id,
            (Facility.name == name_check) | (Facility.slug == slug_check)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Facility with this name or slug already exists"
            )

    for field, value in update_data.items():
        setattr(facility, field, value)

    db.commit()
    db.refresh(facility)
    return {"data": facility, "message": "Facility updated successfully"}

@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(
    facility_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete facility by ID
    Admin only - requires authentication
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if facility is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    db.delete(facility)
    db.commit()
    return None
