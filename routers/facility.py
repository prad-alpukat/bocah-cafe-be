from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil
from datetime import datetime
import uuid
from database import get_db
from models import Facility, Admin
from schemas import FacilityCreate, FacilityUpdate, FacilityResponse, PaginatedResponse, ApiResponse, UploadResponse
from auth_utils import get_current_admin
from firebase_config import upload_file_from_memory, delete_file_from_storage
from config import settings

router = APIRouter()

# Icon upload configuration
ICON_UPLOAD_FOLDER = "facility-icons"
ALLOWED_ICON_EXTENSIONS = {'image/png'}
MAX_ICON_SIZE = settings.MAX_ICON_FILE_SIZE  # 100KB from config

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


# Icon Upload Endpoint
@router.post("/upload-icon", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_facility_icon(
    file: UploadFile = File(..., description="PNG image file (max 100KB, recommended 128x128px)"),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Upload facility icon to Firebase Cloud Storage.
    Admin only - requires authentication.

    Args:
        file: PNG image file (max 100KB)

    Returns:
        UploadResponse: Contains icon URL that can be used in facility.icon field

    Notes:
        - Only PNG format is allowed
        - Maximum file size: 100KB
        - Recommended dimensions: 128x128 pixels
        - The returned URL can be used directly in the facility icon field
    """
    # Validate file type
    if file.content_type not in ALLOWED_ICON_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PNG images are allowed for facility icons"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_ICON_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Icon file too large. Maximum size is {MAX_ICON_SIZE // 1024}KB"
        )

    # Validate PNG signature (first 8 bytes)
    PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
    if not content.startswith(PNG_SIGNATURE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PNG file. File must be a valid PNG image"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.png"
    destination_path = f"{ICON_UPLOAD_FOLDER}/{unique_filename}"

    try:
        icon_url = upload_file_from_memory(
            file_content=content,
            destination_blob_name=destination_path,
            content_type="image/png"
        )

        return {
            "message": "Facility icon uploaded successfully",
            "data": {
                "url": icon_url,
                "filename": unique_filename,
                "original_filename": file.filename,
                "size": len(content),
                "content_type": "image/png",
                "uploaded_by": current_admin.username,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload icon: {str(e)}"
        )


@router.delete("/icon/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facility_icon(
    filename: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete facility icon from Firebase Cloud Storage.
    Admin only - requires authentication.

    Args:
        filename: The icon filename to delete (e.g., 'abc123.png')
    """
    # Security: Only allow deletion from the fixed icon folder
    if not filename.endswith('.png'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename. Must be a PNG file"
        )

    blob_name = f"{ICON_UPLOAD_FOLDER}/{filename}"

    try:
        success = delete_file_from_storage(blob_name)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Icon not found or already deleted"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete icon: {str(e)}"
        )
