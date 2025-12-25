from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, asc, desc
from typing import Optional, Literal
from math import ceil
from database import get_db
from models import Cafe, Admin, Facility
from schemas import CafeCreate, CafeUpdate, CafeResponse, PaginatedResponse, ApiResponse
from auth_utils import get_current_admin

router = APIRouter()

# Valid sort fields
SORT_FIELDS = {
    "rating": Cafe.rating,
    "nama": Cafe.nama,
    "reviews": Cafe.count_google_review,
    "terbaru": Cafe.created_at
}


# Public endpoint - List all cafes
@router.get("/", response_model=PaginatedResponse[CafeResponse])
def get_all_cafes(
    # Pagination
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),

    # Search
    search: Optional[str] = Query(None, description="Search in cafe name and address"),

    # Filters
    nama: Optional[str] = Query(None, description="Filter by cafe name"),
    alamat: Optional[str] = Query(None, description="Filter by address"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating (0-5)"),
    max_rating: Optional[float] = Query(None, ge=0, le=5, description="Maximum rating (0-5)"),
    min_reviews: Optional[int] = Query(None, ge=0, description="Minimum number of Google reviews"),
    facility_slugs: Optional[str] = Query(None, description="Filter by facility slugs (comma-separated, e.g., 'wifi,mushola,ac')"),

    # Sorting
    sort_by: Literal["rating", "nama", "reviews", "terbaru"] = Query("rating", description="Sort by field"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order"),

    db: Session = Depends(get_db)
):
    """
    Get list of all cafes with pagination, filtering, and sorting.
    Public endpoint - no authentication required.

    **Search:** Use `search` to find cafes by name or address.

    **Filters:**
    - `nama`: Filter by cafe name (partial match)
    - `alamat`: Filter by address (partial match)
    - `min_rating` / `max_rating`: Filter by rating range
    - `min_reviews`: Filter popular cafes by minimum review count
    - `facility_slugs`: Filter by facilities (comma-separated)

    **Sorting:**
    - `sort_by`: rating, nama, reviews, terbaru
    - `sort_order`: asc, desc
    """
    query = db.query(Cafe).options(joinedload(Cafe.facilities))

    # Search filter (searches in nama AND alamat)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Cafe.nama.ilike(search_term),
                Cafe.alamat_lengkap.ilike(search_term)
            )
        )

    # Individual filters
    if nama:
        query = query.filter(Cafe.nama.ilike(f"%{nama}%"))

    if alamat:
        query = query.filter(Cafe.alamat_lengkap.ilike(f"%{alamat}%"))

    if min_rating is not None:
        query = query.filter(Cafe.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(Cafe.rating <= max_rating)

    if min_reviews is not None:
        query = query.filter(Cafe.count_google_review >= min_reviews)

    # Facility filter
    if facility_slugs:
        slugs = [s.strip() for s in facility_slugs.split(",") if s.strip()]
        for slug in slugs:
            query = query.filter(Cafe.facilities.any(Facility.slug == slug))

    # Get total count before pagination
    total = query.distinct().count()

    # Apply sorting
    sort_column = SORT_FIELDS.get(sort_by, Cafe.rating)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column).nulls_last(), Cafe.nama)
    else:
        query = query.order_by(asc(sort_column).nulls_last(), Cafe.nama)

    # Pagination
    offset = (page - 1) * page_size
    cafes = query.distinct().offset(offset).limit(page_size).all()

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
@router.get("/{cafe_id}", response_model=ApiResponse[CafeResponse])
def get_cafe(cafe_id: str, db: Session = Depends(get_db)):
    """
    Get single cafe by ID
    Public endpoint - no authentication required
    """
    cafe = db.query(Cafe).options(joinedload(Cafe.facilities)).filter(Cafe.id == cafe_id).first()
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )
    return {"data": cafe}

# Admin only endpoints - Require authentication
@router.post("/", response_model=ApiResponse[CafeResponse], status_code=status.HTTP_201_CREATED)
def create_cafe(
    cafe: CafeCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create new cafe data
    Admin only - requires authentication
    """
    cafe_data = cafe.model_dump(exclude={'facility_ids'})
    new_cafe = Cafe(**cafe_data)

    # Add facilities if provided
    if cafe.facility_ids:
        facilities = db.query(Facility).filter(Facility.id.in_(cafe.facility_ids)).all()
        if len(facilities) != len(cafe.facility_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more facility IDs are invalid"
            )
        new_cafe.facilities = facilities

    db.add(new_cafe)
    db.commit()
    db.refresh(new_cafe)
    return {"data": new_cafe, "message": "Cafe created successfully"}

@router.put("/{cafe_id}", response_model=ApiResponse[CafeResponse])
def update_cafe(
    cafe_id: str,
    cafe_update: CafeUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update cafe data by ID
    Admin only - requires authentication
    """
    cafe = db.query(Cafe).options(joinedload(Cafe.facilities)).filter(Cafe.id == cafe_id).first()
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafe not found"
        )

    # Update only provided fields
    update_data = cafe_update.model_dump(exclude_unset=True)

    # Handle facilities separately
    if 'facility_ids' in update_data:
        facility_ids = update_data.pop('facility_ids')
        if facility_ids is not None:
            facilities = db.query(Facility).filter(Facility.id.in_(facility_ids)).all()
            if len(facilities) != len(facility_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more facility IDs are invalid"
                )
            cafe.facilities = facilities

    for field, value in update_data.items():
        setattr(cafe, field, value)

    db.commit()
    db.refresh(cafe)
    return {"data": cafe, "message": "Cafe updated successfully"}

@router.delete("/{cafe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cafe(
    cafe_id: str,
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
