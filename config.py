from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALLOW_ADMIN_REGISTRATION: bool = True  # Set to False to disable admin registration

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./bocah_cafe.db"

    # Firebase Configuration
    FIREBASE_STORAGE_BUCKET: str = "your-project-id.appspot.com"
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "firebase-key.json"
    FIREBASE_CREDENTIALS: Optional[str] = None  # JSON string for cloud deployment

    # AI Configuration
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
