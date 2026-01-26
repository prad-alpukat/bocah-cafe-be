import ssl
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

DATABASE_URL = settings.DATABASE_URL

# SQLite needs check_same_thread=False, MySQL doesn't need it
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
elif DATABASE_URL.startswith("libsql"):
    # Turso database connection using sqlalchemy-libsql driver
    # URL format: libsql://your-db.turso.io?authToken=xxx
    TURSO_AUTH_TOKEN = settings.TURSO_AUTH_TOKEN

    # Append auth token to URL for sqlalchemy-libsql driver
    db_url = f"{DATABASE_URL}?authToken={TURSO_AUTH_TOKEN}&secure=true"

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    # Configure SSL for Azure MySQL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"ssl": ssl_context},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
