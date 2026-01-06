"""
Permission seeder - Creates default permissions and assigns them to roles
"""
from sqlalchemy.orm import Session
from models import Permission, Role
from .base_seeder import BaseSeeder


class PermissionSeeder(BaseSeeder):
    """Seeder for default permissions"""

    @property
    def name(self) -> str:
        return "Permissions"

    # All available permissions
    PERMISSIONS = [
        # Cafe permissions
        {"name": "View Cafes", "slug": "cafe:read", "resource": "cafe", "action": "read",
         "description": "Can view cafe listings and details"},
        {"name": "Create Cafe", "slug": "cafe:create", "resource": "cafe", "action": "create",
         "description": "Can create new cafes"},
        {"name": "Update Cafe", "slug": "cafe:update", "resource": "cafe", "action": "update",
         "description": "Can update existing cafes"},
        {"name": "Delete Cafe", "slug": "cafe:delete", "resource": "cafe", "action": "delete",
         "description": "Can delete cafes"},
        {"name": "Bulk Import Cafes", "slug": "cafe:bulk_import", "resource": "cafe", "action": "bulk_import",
         "description": "Can bulk import multiple cafes"},

        # Facility permissions
        {"name": "View Facilities", "slug": "facility:read", "resource": "facility", "action": "read",
         "description": "Can view facility listings"},
        {"name": "Create Facility", "slug": "facility:create", "resource": "facility", "action": "create",
         "description": "Can create new facilities"},
        {"name": "Update Facility", "slug": "facility:update", "resource": "facility", "action": "update",
         "description": "Can update existing facilities"},
        {"name": "Delete Facility", "slug": "facility:delete", "resource": "facility", "action": "delete",
         "description": "Can delete facilities"},
        {"name": "Upload Facility Icon", "slug": "facility:upload_icon", "resource": "facility", "action": "upload_icon",
         "description": "Can upload facility icons"},

        # Collection permissions
        {"name": "View Collections", "slug": "collection:read", "resource": "collection", "action": "read",
         "description": "Can view collection listings"},
        {"name": "Create Collection", "slug": "collection:create", "resource": "collection", "action": "create",
         "description": "Can create new collections"},
        {"name": "Update Collection", "slug": "collection:update", "resource": "collection", "action": "update",
         "description": "Can update existing collections"},
        {"name": "Delete Collection", "slug": "collection:delete", "resource": "collection", "action": "delete",
         "description": "Can delete collections"},
        {"name": "Manage Collection Cafes", "slug": "collection:manage_cafes", "resource": "collection", "action": "manage_cafes",
         "description": "Can add/remove cafes from collections"},

        # Admin management permissions
        {"name": "View Admins", "slug": "admin:read", "resource": "admin", "action": "read",
         "description": "Can view admin listings"},
        {"name": "Create Admin", "slug": "admin:create", "resource": "admin", "action": "create",
         "description": "Can create new admin users"},
        {"name": "Update Admin", "slug": "admin:update", "resource": "admin", "action": "update",
         "description": "Can update admin users"},
        {"name": "Delete Admin", "slug": "admin:delete", "resource": "admin", "action": "delete",
         "description": "Can delete admin users"},

        # Role management permissions
        {"name": "View Roles", "slug": "role:read", "resource": "role", "action": "read",
         "description": "Can view role listings"},
        {"name": "Create Role", "slug": "role:create", "resource": "role", "action": "create",
         "description": "Can create new roles"},
        {"name": "Update Role", "slug": "role:update", "resource": "role", "action": "update",
         "description": "Can update existing roles"},
        {"name": "Delete Role", "slug": "role:delete", "resource": "role", "action": "delete",
         "description": "Can delete roles"},
        {"name": "Manage Role Permissions", "slug": "role:manage_permissions", "resource": "role", "action": "manage_permissions",
         "description": "Can assign/remove permissions from roles"},

        # Permission management
        {"name": "View Permissions", "slug": "permission:read", "resource": "permission", "action": "read",
         "description": "Can view permission listings"},

        # Upload permissions
        {"name": "Upload Images", "slug": "upload:image", "resource": "upload", "action": "image",
         "description": "Can upload images to storage"},
        {"name": "Delete Uploaded Images", "slug": "upload:delete", "resource": "upload", "action": "delete",
         "description": "Can delete uploaded images"},

        # Search permissions (usually public, but can be restricted)
        {"name": "Use Search", "slug": "search:use", "resource": "search", "action": "use",
         "description": "Can use natural language search"},
    ]

    # Role permission assignments (superadmin gets all by default)
    ROLE_PERMISSIONS = {
        "admin": [
            # Cafe - full access
            "cafe:read", "cafe:create", "cafe:update", "cafe:delete", "cafe:bulk_import",
            # Facility - full access
            "facility:read", "facility:create", "facility:update", "facility:delete", "facility:upload_icon",
            # Collection - full access
            "collection:read", "collection:create", "collection:update", "collection:delete", "collection:manage_cafes",
            # Admin - view only
            "admin:read",
            # Role - view only
            "role:read",
            # Permission - view only
            "permission:read",
            # Upload - full access
            "upload:image", "upload:delete",
            # Search
            "search:use",
        ],
        "writer": [
            # Cafe - create and update only
            "cafe:read", "cafe:create", "cafe:update",
            # Facility - read only
            "facility:read",
            # Collection - create and update only
            "collection:read", "collection:create", "collection:update", "collection:manage_cafes",
            # Upload - can upload
            "upload:image",
            # Search
            "search:use",
        ],
        "viewer": [
            # Read-only access to everything
            "cafe:read",
            "facility:read",
            "collection:read",
            "search:use",
        ]
    }

    def run(self) -> None:
        """Create permissions and assign to roles"""
        # Step 1: Create all permissions
        self.log("Creating permissions...")
        permission_map = {}  # slug -> Permission object

        for perm_data in self.PERMISSIONS:
            existing = self.db.query(Permission).filter(
                Permission.slug == perm_data["slug"]
            ).first()

            if existing:
                permission_map[perm_data["slug"]] = existing
                self.log(f"Permission '{perm_data['slug']}' already exists", "skip")
            else:
                permission = Permission(**perm_data)
                self.db.add(permission)
                self.db.flush()
                permission_map[perm_data["slug"]] = permission
                self.log(f"Created permission '{perm_data['slug']}'", "success")

        self.db.commit()

        # Step 2: Assign permissions to roles
        self.log("\nAssigning permissions to roles...")

        for role_slug, permission_slugs in self.ROLE_PERMISSIONS.items():
            role = self.db.query(Role).filter(Role.slug == role_slug).first()

            if not role:
                self.log(f"Role '{role_slug}' not found, skipping", "warning")
                continue

            # Get current permissions
            current_permission_slugs = {p.slug for p in role.permissions}

            # Add new permissions
            added_count = 0
            for perm_slug in permission_slugs:
                if perm_slug not in current_permission_slugs:
                    permission = permission_map.get(perm_slug)
                    if permission:
                        role.permissions.append(permission)
                        added_count += 1

            if added_count > 0:
                self.log(f"Added {added_count} permissions to role '{role_slug}'", "success")
            else:
                self.log(f"Role '{role_slug}' already has all assigned permissions", "skip")

        self.db.commit()
        self.log(f"\nTotal permissions: {len(self.PERMISSIONS)}", "info")
