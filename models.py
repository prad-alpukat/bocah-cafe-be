from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association table for many-to-many relationship between Cafe and Facility
cafe_facilities = Table(
    'cafe_facilities',
    Base.metadata,
    Column('cafe_id', Integer, ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True),
    Column('facility_id', Integer, ForeignKey('facilities.id', ondelete='CASCADE'), primary_key=True)
)

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    icon = Column(String, nullable=True)  # Icon name or URL
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    cafes = relationship("Cafe", secondary=cafe_facilities, back_populates="facilities")

class Cafe(Base):
    __tablename__ = "cafes"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, index=True, nullable=False)
    gambar_thumbnail = Column(String)
    no_hp = Column(String)
    link_website = Column(String)
    rating = Column(Float)
    range_price = Column(String)
    count_google_review = Column(Integer)
    jam_buka = Column(String)
    alamat_lengkap = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    facilities = relationship("Facility", secondary=cafe_facilities, back_populates="cafes")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    admins = relationship("Admin", back_populates="role")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    role = relationship("Role", back_populates="admins")
