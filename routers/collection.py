from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, Literal
from math import ceil
from database import get_db
from models import Collection, Cafe, Admin
from schemas import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionDetailResponse,
    CollectionAccessRequest,
    CollectionAccessResponse,
    CollectionCafesUpdate,
    CafeResponse,
    PaginatedResponse,
    ApiResponse,
    MessageResponse
)
from auth_utils import get_current_admin, get_password_hash, verify_password

router = APIRouter()


def collection_to_response(collection: Collection, include_cafes: bool = False):
    """Convert Collection model to response dict with cafe_count"""
    response = {
        "id": collection.id,
        "name": collection.name,
        "slug": collection.slug,
        "description": collection.description,
        "gambar_cover": collection.gambar_cover,
        "visibility": collection.visibility,
        "cafe_count": len(collection.cafes) if collection.cafes else 0,
        "created_at": collection.created_at,
        "updated_at": collection.updated_at,
    }
    if include_cafes:
        response["cafes"] = collection.cafes
    return response


# =====================
# PUBLIC ENDPOINTS
# =====================

@router.get("/", response_model=PaginatedResponse[CollectionResponse])
def get_public_collections(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: Session = Depends(get_db)
):
    """
    Get list of public collections (visibility = 'public' or 'password_protected')
    Public endpoint - no authentication required
    """
    query = db.query(Collection).options(joinedload(Collection.cafes))

    # Only show public and password_protected collections
    query = query.filter(Collection.visibility.in_(['public', 'password_protected']))

    # Search filter
    if search:
        query = query.filter(Collection.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Order and paginate
    query = query.order_by(Collection.created_at.desc())
    offset = (page - 1) * page_size
    collections = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return {
        "data": [collection_to_response(c) for c in collections],
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }


@router.get("/slug/{slug}", response_model=ApiResponse[CollectionDetailResponse])
def get_collection_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Get collection by slug (public collections only, shows cafes)
    For password_protected, use /access endpoint
    Public endpoint - no authentication required
    """
    collection = db.query(Collection).options(
        joinedload(Collection.cafes).joinedload(Cafe.facilities)
    ).filter(Collection.slug == slug).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    # Only allow public collections
    if collection.visibility == 'private':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This collection is private"
        )

    # For password_protected, don't show cafes
    if collection.visibility == 'password_protected':
        response = collection_to_response(collection, include_cafes=False)
        response["cafes"] = []  # Hide cafes for password protected
        return {"data": response, "message": "Password required to view cafes"}

    return {"data": collection_to_response(collection, include_cafes=True)}


@router.get("/{collection_id}", response_model=ApiResponse[CollectionDetailResponse])
def get_collection_by_id(collection_id: str, db: Session = Depends(get_db)):
    """
    Get collection by ID (public collections only, shows cafes)
    For password_protected, use /access endpoint
    Public endpoint - no authentication required
    """
    collection = db.query(Collection).options(
        joinedload(Collection.cafes).joinedload(Cafe.facilities)
    ).filter(Collection.id == collection_id).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    # Only allow public collections
    if collection.visibility == 'private':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This collection is private"
        )

    # For password_protected, don't show cafes
    if collection.visibility == 'password_protected':
        response = collection_to_response(collection, include_cafes=False)
        response["cafes"] = []
        return {"data": response, "message": "Password required to view cafes"}

    return {"data": collection_to_response(collection, include_cafes=True)}


@router.post("/{collection_id}/access", response_model=CollectionAccessResponse)
def access_protected_collection(
    collection_id: str,
    access_request: CollectionAccessRequest,
    db: Session = Depends(get_db)
):
    """
    Verify password and get access to password-protected collection
    Public endpoint - no authentication required
    """
    collection = db.query(Collection).options(
        joinedload(Collection.cafes).joinedload(Cafe.facilities)
    ).filter(Collection.id == collection_id).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    if collection.visibility != 'password_protected':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This collection is not password protected"
        )

    # Verify password
    if not collection.password_hash or not verify_password(access_request.password, collection.password_hash):
        return CollectionAccessResponse(
            access_granted=False,
            collection=None,
            message="Invalid password"
        )

    return CollectionAccessResponse(
        access_granted=True,
        collection=collection_to_response(collection, include_cafes=True),
        message="Access granted"
    )


# =====================
# ADMIN ENDPOINTS
# =====================

@router.get("/admin/all", response_model=PaginatedResponse[CollectionResponse])
def get_all_collections_admin(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name"),
    visibility: Optional[Literal['public', 'private', 'password_protected']] = Query(None, description="Filter by visibility"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get all collections including private ones
    Admin only - requires authentication
    """
    query = db.query(Collection).options(joinedload(Collection.cafes))

    # Filter by visibility
    if visibility:
        query = query.filter(Collection.visibility == visibility)

    # Search filter
    if search:
        query = query.filter(Collection.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Order and paginate
    query = query.order_by(Collection.created_at.desc())
    offset = (page - 1) * page_size
    collections = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return {
        "data": [collection_to_response(c) for c in collections],
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }


@router.get("/admin/{collection_id}", response_model=ApiResponse[CollectionDetailResponse])
def get_collection_admin(
    collection_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get collection by ID (admin access - can see all including private)
    Admin only - requires authentication
    """
    collection = db.query(Collection).options(
        joinedload(Collection.cafes).joinedload(Cafe.facilities)
    ).filter(Collection.id == collection_id).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    return {"data": collection_to_response(collection, include_cafes=True)}


@router.post("/", response_model=ApiResponse[CollectionResponse], status_code=status.HTTP_201_CREATED)
def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create new collection
    Admin only - requires authentication
    """
    # Check if slug already exists
    existing = db.query(Collection).filter(Collection.slug == collection_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection with this slug already exists"
        )

    # Prepare data
    data = collection_data.model_dump(exclude={'password', 'cafe_ids'})

    # Hash password if provided
    if collection_data.visibility == 'password_protected' and collection_data.password:
        data['password_hash'] = get_password_hash(collection_data.password)

    # Create collection
    new_collection = Collection(**data)

    # Add cafes if provided
    if collection_data.cafe_ids:
        cafes = db.query(Cafe).filter(Cafe.id.in_(collection_data.cafe_ids)).all()
        if len(cafes) != len(collection_data.cafe_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more cafe IDs are invalid"
            )
        new_collection.cafes = cafes

    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    return {"data": collection_to_response(new_collection), "message": "Collection created successfully"}


@router.put("/{collection_id}", response_model=ApiResponse[CollectionResponse])
def update_collection(
    collection_id: str,
    collection_update: CollectionUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update collection
    Admin only - requires authentication
    """
    collection = db.query(Collection).options(
        joinedload(Collection.cafes)
    ).filter(Collection.id == collection_id).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    update_data = collection_update.model_dump(exclude_unset=True)

    # Check slug uniqueness if updating
    if 'slug' in update_data and update_data['slug'] != collection.slug:
        existing = db.query(Collection).filter(
            Collection.slug == update_data['slug'],
            Collection.id != collection_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Collection with this slug already exists"
            )

    # Handle password update
    if 'password' in update_data:
        password = update_data.pop('password')
        if password:
            update_data['password_hash'] = get_password_hash(password)

    # Handle cafe_ids update
    if 'cafe_ids' in update_data:
        cafe_ids = update_data.pop('cafe_ids')
        if cafe_ids is not None:
            cafes = db.query(Cafe).filter(Cafe.id.in_(cafe_ids)).all()
            if len(cafes) != len(cafe_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more cafe IDs are invalid"
                )
            collection.cafes = cafes

    # Validate password requirement for password_protected
    new_visibility = update_data.get('visibility', collection.visibility)
    if new_visibility == 'password_protected' and not collection.password_hash and 'password_hash' not in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for password_protected visibility"
        )

    # Update other fields
    for field, value in update_data.items():
        setattr(collection, field, value)

    db.commit()
    db.refresh(collection)

    return {"data": collection_to_response(collection), "message": "Collection updated successfully"}


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete collection
    Admin only - requires authentication
    """
    collection = db.query(Collection).filter(Collection.id == collection_id).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    db.delete(collection)
    db.commit()
    return None


@router.post("/{collection_id}/cafes", response_model=ApiResponse[CollectionDetailResponse])
def add_cafes_to_collection(
    collection_id: str,
    cafes_update: CollectionCafesUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Add cafes to collection
    Admin only - requires authentication
    """
    collection = db.query(Collection).options(
        joinedload(Collection.cafes).joinedload(Cafe.facilities)
    ).filter(Collection.id == collection_id).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    # Get cafes to add
    cafes_to_add = db.query(Cafe).filter(Cafe.id.in_(cafes_update.cafe_ids)).all()
    if len(cafes_to_add) != len(cafes_update.cafe_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more cafe IDs are invalid"
        )

    # Get current cafe IDs
    current_cafe_ids = {c.id for c in collection.cafes}

    # Add only new cafes
    added_count = 0
    for cafe in cafes_to_add:
        if cafe.id not in current_cafe_ids:
            collection.cafes.append(cafe)
            added_count += 1

    db.commit()
    db.refresh(collection)

    return {
        "data": collection_to_response(collection, include_cafes=True),
        "message": f"Added {added_count} cafe(s) to collection"
    }


@router.delete("/{collection_id}/cafes", response_model=ApiResponse[CollectionDetailResponse])
def remove_cafes_from_collection(
    collection_id: str,
    cafes_update: CollectionCafesUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Remove cafes from collection
    Admin only - requires authentication
    """
    collection = db.query(Collection).options(
        joinedload(Collection.cafes).joinedload(Cafe.facilities)
    ).filter(Collection.id == collection_id).first()

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )

    # Remove specified cafes
    cafe_ids_to_remove = set(cafes_update.cafe_ids)
    removed_count = 0
    collection.cafes = [c for c in collection.cafes if c.id not in cafe_ids_to_remove]
    removed_count = len(cafe_ids_to_remove)

    db.commit()
    db.refresh(collection)

    return {
        "data": collection_to_response(collection, include_cafes=True),
        "message": f"Removed cafe(s) from collection"
    }
