"""
Base seeder class with common functionality
"""
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


class BaseSeeder(ABC):
    """Abstract base class for all seeders"""

    def __init__(self, db: Session):
        self.db = db

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the seeder name for display purposes"""
        pass

    @abstractmethod
    def run(self) -> None:
        """Execute the seeder"""
        pass

    def log(self, message: str, status: str = "info") -> None:
        """Print formatted log message"""
        icons = {
            "info": " ",
            "success": "✓",
            "warning": "!",
            "error": "✗",
            "skip": "→"
        }
        icon = icons.get(status, " ")
        print(f"  {icon} {message}")
