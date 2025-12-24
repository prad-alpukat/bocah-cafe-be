from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from math import ceil
import re

# Generic Response Schemas
T = TypeVar('T')

class PaginationMeta(BaseModel):
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

class PaginatedResponse(BaseModel, Generic[T]):
    """Response wrapper for paginated list endpoints"""
    data: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

class ApiResponse(BaseModel, Generic[T]):
    """Response wrapper for single item endpoints (GET by ID, POST, PUT)"""
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional message")

class MessageResponse(BaseModel):
    """Response for operations that only return a message (e.g., delete confirmation)"""
    message: str = Field(..., description="Response message")

class UploadResponse(BaseModel):
    """Response for file upload operations"""
    data: dict = Field(..., description="Upload details")
    message: str = Field(..., description="Success message")

# Facility Schemas
class FacilityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nama fasilitas")
    slug: str = Field(..., min_length=2, max_length=100, description="Slug fasilitas (lowercase, alphanumeric with hyphens)")
    icon: Optional[str] = Field(None, max_length=255, description="Nama icon atau URL icon")
    description: Optional[str] = Field(None, max_length=500, description="Deskripsi fasilitas")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

class FacilityCreate(FacilityBase):
    pass

class FacilityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    icon: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

class FacilityResponse(FacilityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Cafe Schemas
class CafeBase(BaseModel):
    nama: str = Field(..., description="Nama cafe")
    gambar_thumbnail: Optional[str] = Field(None, description="URL gambar thumbnail")
    no_hp: Optional[str] = Field(None, description="Nomor HP/telepon")
    link_website: Optional[str] = Field(None, description="Link website")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating (0-5)")
    range_price: Optional[str] = Field(None, description="Range harga (misal: Rp 10.000 - Rp 50.000)")
    count_google_review: Optional[int] = Field(None, ge=0, description="Jumlah review Google")
    jam_buka: Optional[str] = Field(None, description="Jam buka")
    alamat_lengkap: Optional[str] = Field(None, description="Alamat lengkap")

class CafeCreate(CafeBase):
    facility_ids: Optional[List[int]] = Field(None, description="List of facility IDs")

class CafeUpdate(BaseModel):
    nama: Optional[str] = None
    gambar_thumbnail: Optional[str] = None
    no_hp: Optional[str] = None
    link_website: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    range_price: Optional[str] = None
    count_google_review: Optional[int] = Field(None, ge=0)
    jam_buka: Optional[str] = None
    alamat_lengkap: Optional[str] = None
    facility_ids: Optional[List[int]] = Field(None, description="List of facility IDs to replace current facilities")

class CafeResponse(CafeBase):
    id: int
    facilities: List[FacilityResponse] = Field(default_factory=list, description="List of facilities")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Role name")
    slug: str = Field(..., min_length=2, max_length=50, description="Role slug (lowercase, alphanumeric with hyphens)")
    description: Optional[str] = Field(None, max_length=500, description="Role description")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

class RoleResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    is_system_role: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Auth Schemas
class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role_id: int = Field(..., description="Role ID")

class AdminResponse(BaseModel):
    id: int
    username: str
    role: RoleResponse
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role_id: Optional[int] = None
    role_slug: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Admin Management Schemas
class AdminUpdateRole(BaseModel):
    role_id: int = Field(..., description="New role ID for admin")

class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[int] = None

class AdminListResponse(BaseModel):
    id: int
    username: str
    role: RoleResponse
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
