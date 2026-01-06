from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Generic, TypeVar, Literal
from datetime import datetime
from math import ceil
import re
from urllib.parse import urlparse
from config import settings


def validate_icon_format(icon: Optional[str]) -> Optional[str]:
    """
    Validate icon format. Accepts:
    1. Iconify format: iconify:{icon-set}:{icon-name}
       Example: iconify:lucide:wifi, iconify:mdi:parking
    2. PNG URL format: https:// URL from allowed domains
       Example: https://storage.googleapis.com/bucket/icon.png
    3. None/empty string

    Rejects:
    - Raw SVG strings (XSS risk)
    - URLs from non-allowed domains
    - Invalid formats
    """
    if icon is None or icon.strip() == "":
        return None

    icon = icon.strip()

    # Check for Iconify format
    if icon.startswith("iconify:"):
        # Format: iconify:{set}:{name}
        parts = icon.split(":")
        if len(parts) != 3:
            raise ValueError(
                "Invalid Iconify format. Use: iconify:{icon-set}:{icon-name} "
                "(e.g., iconify:lucide:wifi)"
            )
        icon_set, icon_name = parts[1], parts[2]
        if not icon_set or not icon_name:
            raise ValueError(
                "Iconify icon-set and icon-name cannot be empty"
            )
        # Validate icon set and name characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', icon_set):
            raise ValueError(f"Invalid icon-set: {icon_set}")
        if not re.match(r'^[a-zA-Z0-9_-]+$', icon_name):
            raise ValueError(f"Invalid icon-name: {icon_name}")
        return icon

    # Check for URL format
    if icon.startswith("http://") or icon.startswith("https://"):
        # Must be HTTPS
        if icon.startswith("http://"):
            raise ValueError("Icon URL must use HTTPS")

        # Parse URL
        try:
            parsed = urlparse(icon)
        except Exception:
            raise ValueError("Invalid icon URL format")

        # Check allowed domains
        allowed_domains = [d.strip() for d in settings.ALLOWED_ICON_DOMAINS.split(",")]
        if parsed.netloc not in allowed_domains:
            raise ValueError(
                f"Icon URL domain not allowed. Allowed domains: {', '.join(allowed_domains)}"
            )

        # Check file extension (must be PNG)
        if not parsed.path.lower().endswith('.png'):
            raise ValueError("Icon URL must point to a PNG file")

        return icon

    # Check for raw SVG (security risk - reject)
    if icon.startswith("<svg") or icon.startswith("<?xml") or "xmlns" in icon.lower():
        raise ValueError("Raw SVG is not allowed for security reasons. Use Iconify format or upload PNG.")

    # Invalid format
    raise ValueError(
        "Invalid icon format. Use either:\n"
        "1. Iconify: iconify:{set}:{name} (e.g., iconify:lucide:wifi)\n"
        "2. PNG URL: https:// URL from allowed storage domain"
    )

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
    icon: Optional[str] = Field(
        None,
        max_length=500,
        description="Icon dalam format Iconify (iconify:set:name) atau URL PNG dari storage"
    )
    description: Optional[str] = Field(None, max_length=500, description="Deskripsi fasilitas")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        return validate_icon_format(v)

class FacilityCreate(FacilityBase):
    pass

class FacilityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    icon: Optional[str] = Field(
        None,
        max_length=500,
        description="Icon dalam format Iconify (iconify:set:name) atau URL PNG dari storage"
    )
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_icon_format(v)
        return v

class FacilityResponse(FacilityBase):
    id: str
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
    facility_ids: Optional[List[str]] = Field(None, description="List of facility IDs")

# Bulk Import Schemas
class CafeBulkItem(CafeBase):
    """Single cafe item for bulk import - uses facility slugs instead of IDs"""
    facility_slugs: Optional[List[str]] = Field(None, description="List of facility slugs (e.g., ['wifi', 'ac', 'mushola'])")

class CafeBulkCreate(BaseModel):
    """Request body for bulk cafe import"""
    cafes: List[CafeBulkItem] = Field(..., min_length=1, max_length=500, description="List of cafes to import (max 500)")
    skip_duplicates: bool = Field(default=True, description="Skip cafes with duplicate names instead of failing")

class CafeBulkResultItem(BaseModel):
    """Result for a single cafe in bulk import"""
    nama: str
    success: bool
    id: Optional[str] = None
    error: Optional[str] = None

class CafeBulkResponse(BaseModel):
    """Response for bulk cafe import"""
    total: int = Field(..., description="Total cafes in request")
    created: int = Field(..., description="Successfully created")
    skipped: int = Field(..., description="Skipped (duplicates)")
    failed: int = Field(..., description="Failed to create")
    results: List[CafeBulkResultItem] = Field(..., description="Result for each cafe")

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
    facility_ids: Optional[List[str]] = Field(None, description="List of facility IDs to replace current facilities")

class CafeResponse(CafeBase):
    id: str
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
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    is_system_role: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Permission Schemas
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Permission name (e.g., 'Create Cafe')")
    slug: str = Field(..., min_length=3, max_length=100, description="Permission slug (e.g., 'cafe:create')")
    resource: str = Field(..., min_length=2, max_length=50, description="Resource name (e.g., 'cafe', 'admin')")
    action: str = Field(..., min_length=2, max_length=50, description="Action name (e.g., 'create', 'delete')")
    description: Optional[str] = Field(None, max_length=500, description="Permission description")

    @field_validator('slug')
    @classmethod
    def validate_permission_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9]+:[a-z0-9_]+$', v):
            raise ValueError('Permission slug must be in format resource:action (e.g., cafe:create)')
        return v


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(BaseModel):
    id: str
    name: str
    slug: str
    resource: str
    action: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoleWithPermissionsResponse(BaseModel):
    """Role response with permissions included"""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    is_system_role: bool
    permissions: List[PermissionResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RolePermissionsUpdate(BaseModel):
    """Request to update role permissions"""
    permission_ids: List[str] = Field(..., description="List of permission IDs to assign to role")


class RolePermissionsSlugsUpdate(BaseModel):
    """Request to update role permissions using slugs"""
    permission_slugs: List[str] = Field(..., description="List of permission slugs to assign (e.g., ['cafe:create', 'cafe:update'])")


class RoleSummary(BaseModel):
    """Minimal role info for permission response"""
    id: str
    name: str
    slug: str

    class Config:
        from_attributes = True


class MyPermissionsResponse(BaseModel):
    """Response for current user's permissions"""
    role: RoleSummary
    is_superadmin: bool = Field(default=False, description="True if user is superadmin (has all permissions)")
    permissions: List[PermissionResponse] = Field(default_factory=list, description="List of assigned permissions")

    class Config:
        from_attributes = True


# Auth Schemas
class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role_id: str = Field(..., description="Role ID")

class AdminResponse(BaseModel):
    id: str
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
    role_id: Optional[str] = None
    role_slug: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Admin Management Schemas
class AdminUpdateRole(BaseModel):
    role_id: str = Field(..., description="New role ID for admin")

class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[str] = None

class AdminListResponse(BaseModel):
    id: str
    username: str
    role: RoleResponse
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Collection Schemas
class CollectionBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nama koleksi")
    slug: str = Field(..., min_length=2, max_length=100, description="Slug koleksi (lowercase, alphanumeric with hyphens)")
    description: Optional[str] = Field(None, max_length=1000, description="Deskripsi koleksi")
    gambar_cover: Optional[str] = Field(None, description="URL gambar cover")
    visibility: Literal['public', 'private', 'password_protected'] = Field(
        default='public',
        description="Visibility: public, private, atau password_protected"
    )

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

class CollectionCreate(CollectionBase):
    password: Optional[str] = Field(None, min_length=4, description="Password untuk visibility password_protected")
    cafe_ids: Optional[List[str]] = Field(None, description="List of cafe IDs to add")

    @model_validator(mode='after')
    def validate_password_required(self):
        if self.visibility == 'password_protected' and not self.password:
            raise ValueError('Password is required when visibility is password_protected')
        return self

class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    gambar_cover: Optional[str] = None
    visibility: Optional[Literal['public', 'private', 'password_protected']] = None
    password: Optional[str] = Field(None, min_length=4, description="New password for password_protected visibility")
    cafe_ids: Optional[List[str]] = Field(None, description="List of cafe IDs to replace current cafes")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must be lowercase alphanumeric with hyphens only')
        return v

class CollectionResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    gambar_cover: Optional[str] = None
    visibility: str
    cafe_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CollectionDetailResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    gambar_cover: Optional[str] = None
    visibility: str
    cafe_count: int = 0
    cafes: List[CafeResponse] = Field(default_factory=list, description="List of cafes in collection")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CollectionAccessRequest(BaseModel):
    password: str = Field(..., description="Password untuk akses koleksi")

class CollectionAccessResponse(BaseModel):
    access_granted: bool
    collection: Optional[CollectionDetailResponse] = None
    message: str

class CollectionCafesUpdate(BaseModel):
    cafe_ids: List[str] = Field(..., min_length=1, description="List of cafe IDs to add/remove")
