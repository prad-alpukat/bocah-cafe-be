"""
Role seeder - Creates default system roles
"""
from sqlalchemy.orm import Session
from models import Role
from .base_seeder import BaseSeeder


class RoleSeeder(BaseSeeder):
    """Seeder for default roles"""

    @property
    def name(self) -> str:
        return "Roles"

    # Default roles data
    ROLES = [
        {
            "name": "Super Admin",
            "slug": "superadmin",
            "description": "Full system access with all permissions",
            "is_system_role": True
        },
        {
            "name": "Admin",
            "slug": "admin",
            "description": "Administrative access for content management",
            "is_system_role": True
        },
        {
            "name": "Writer",
            "slug": "writer",
            "description": "Can create and manage cafe content",
            "is_system_role": True
        },
        {
            "name": "Viewer",
            "slug": "viewer",
            "description": "Read-only access to admin panel",
            "is_system_role": True
        }
    ]

    def run(self) -> None:
        """Create default roles if they don't exist"""
        for role_data in self.ROLES:
            existing = self.db.query(Role).filter(
                Role.slug == role_data["slug"]
            ).first()

            if existing:
                self.log(f"Role '{role_data['name']}' already exists (ID: {existing.id})", "skip")
            else:
                role = Role(**role_data)
                self.db.add(role)
                self.db.flush()
                self.log(f"Created role '{role_data['name']}' (ID: {role.id})", "success")

        self.db.commit()
