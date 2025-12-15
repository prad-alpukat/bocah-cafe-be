from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

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

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
