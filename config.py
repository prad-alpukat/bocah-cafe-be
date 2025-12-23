from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALLOW_ADMIN_REGISTRATION: bool = True  # Set to False to disable admin registration

    # Firebase Configuration
    FIREBASE_STORAGE_BUCKET: str = "your-project-id.appspot.com"
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "path/to/serviceAccountKey.json"

    class Config:
        env_file = ".env"

settings = Settings()
