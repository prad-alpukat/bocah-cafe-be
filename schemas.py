from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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
    pass

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

class CafeResponse(CafeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Auth Schemas
class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class AdminResponse(BaseModel):
    id: int
    username: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
