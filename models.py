from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Association table for many-to-many relationship between Cafe and Facility
cafe_facilities = Table(
    'cafe_facilities',
    Base.metadata,
    Column('cafe_id', String(36), ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True),
    Column('facility_id', String(36), ForeignKey('facilities.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for many-to-many relationship between Collection and Cafe
collection_cafes = Table(
    'collection_cafes',
    Base.metadata,
    Column('collection_id', String(36), ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True),
    Column('cafe_id', String(36), ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True)
)

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    icon = Column(String(500), nullable=True)  # Icon name or URL
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    cafes = relationship("Cafe", secondary=cafe_facilities, back_populates="facilities")

class Cafe(Base):
    __tablename__ = "cafes"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    nama = Column(String(255), index=True, nullable=False)
    gambar_thumbnail = Column(String(500))
    no_hp = Column(String(50))
    link_website = Column(String(500))
    rating = Column(Float)
    range_price = Column(String(100))
    count_google_review = Column(Integer)
    jam_buka = Column(String(255))
    alamat_lengkap = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    facilities = relationship("Facility", secondary=cafe_facilities, back_populates="cafes")
    collections = relationship("Collection", secondary=collection_cafes, back_populates="cafes")

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    admins = relationship("Admin", back_populates="role")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    role = relationship("Role", back_populates="admins")

class Collection(Base):
    __tablename__ = "collections"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    gambar_cover = Column(String(500), nullable=True)

    # Visibility: 'public', 'private', 'password_protected'
    visibility = Column(String(20), default='public', nullable=False)
    password_hash = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    cafes = relationship("Cafe", secondary=collection_cafes, back_populates="collections")
