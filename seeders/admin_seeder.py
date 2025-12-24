"""
Admin seeder - Creates default admin users
"""
from sqlalchemy.orm import Session
from models import Admin, Role
from auth_utils import get_password_hash
from .base_seeder import BaseSeeder


class AdminSeeder(BaseSeeder):
    """Seeder for default admin users"""

    @property
    def name(self) -> str:
        return "Admins"

    # Default admin users data
    ADMINS = [
        {
            "username": "admin",
            "password": "password",
            "role_slug": "superadmin"
        }
    ]

    def run(self) -> None:
        """Create default admin users if they don't exist"""
        for admin_data in self.ADMINS:
            # Check if admin already exists
            existing = self.db.query(Admin).filter(
                Admin.username == admin_data["username"]
            ).first()

            if existing:
                self.log(
                    f"Admin '{admin_data['username']}' already exists (ID: {existing.id})",
                    "skip"
                )
                continue

            # Find the role
            role = self.db.query(Role).filter(
                Role.slug == admin_data["role_slug"]
            ).first()

            if not role:
                self.log(
                    f"Role '{admin_data['role_slug']}' not found. Run RoleSeeder first.",
                    "error"
                )
                continue

            # Create admin
            admin = Admin(
                username=admin_data["username"],
                hashed_password=get_password_hash(admin_data["password"]),
                role_id=role.id
            )
            self.db.add(admin)
            self.db.flush()
            self.log(
                f"Created admin '{admin_data['username']}' with role '{role.name}' (ID: {admin.id})",
                "success"
            )

        self.db.commit()
