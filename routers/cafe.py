from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil
from database import get_db
from models import Cafe, Admin
from schemas import CafeCreate, CafeUpdate, CafeResponse, PaginatedResponse, PaginationMeta
from auth_utils import get_current_admin

router = APIRouter()

# Public endpoint - List all cafes
@router.get("/", response_model=PaginatedResponse[CafeResponse])
def get_all_cafes(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    nama: Optional[str] = Query(None, description="Filter by cafe name"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    db: Session = Depends(get_db)
):
    """
    Get list of all cafes with pagination and optional filtering
    Public endpoint - no authentication required
    """
    query = db.query(Cafe)
    
    # Apply filters
    if nama:
        query = query.filter(Cafe.nama.ilike(f"%{nama}%"))
    if min_rating is not None:
        query = query.filter(Cafe.rating >= min_rating)
    
    # Get total count before pagination
    total = query.count()
    
    # Order by rating descending, then by name
    query = query.order_by(Cafe.rating.desc(), Cafe.nama)
    
    # Calculate offset and apply pagination
    offset = (page - 1) * page_size
    cafes = query.offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return {
        "data": cafes,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }

# Public endpoint - Get single cafe by ID
@router.get("/{cafe_id}", response_model=CafeResponse)
def get_cafe(cafe_id: int, db: Session = Depends(get_db)):
    """
    Get single cafe by ID
    Public endpoint - no authentication required
    """
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    return cafe

# Admin only endpoints - Require authentication
@router.post("/", response_model=CafeResponse, status_code=status.HTTP_201_CREATED)
def create_cafe(
    cafe: CafeCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create new cafe data
    Admin only - requires authentication
    """
    new_cafe = Cafe(**cafe.dict())
    db.add(new_cafe)
    db.commit()
    db.refresh(new_cafe)
    return new_cafe

@router.put("/{cafe_id}", response_model=CafeResponse)
def update_cafe(
    cafe_id: int,
    cafe_update: CafeUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update cafe data by ID
    Admin only - requires authentication
    """
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    
    # Update only provided fields
    update_data = cafe_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cafe, field, value)
    
    db.commit()
    db.refresh(cafe)
    return cafe

@router.delete("/{cafe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cafe(
    cafe_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete cafe by ID
    Admin only - requires authentication
    """
    cafe = db.query(Cafe).filter(Cafe.id == cafe_id).first()
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    
    db.delete(cafe)
    db.commit()
    return None
