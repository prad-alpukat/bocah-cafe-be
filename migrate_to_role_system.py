"""
Migration script to convert from string-based roles to database-based role system
This script will:
1. Create the roles table
2. Create default system roles (superadmin and writer)
3. Migrate existing admins to use role_id
4. Drop the old role column from admins table

Run this once to upgrade to the new role management system
"""
import sqlite3
from pathlib import Path
from datetime import datetime

def migrate_to_role_system():
    db_path = Path(__file__).parent / "bocah_cafe.db"

    if not db_path.exists():
        print("✗ Database file not found. Please create the database first.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Starting migration to role system...")
        print("-" * 50)

        # Step 1: Check if roles table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='roles'
        """)

        if cursor.fetchone():
            print("✓ Roles table already exists. Checking for default roles...")
        else:
            # Create roles table
            print("Creating roles table...")
            cursor.execute("""
                CREATE TABLE roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR NOT NULL UNIQUE,
                    slug VARCHAR NOT NULL UNIQUE,
                    description TEXT,
                    is_system_role BOOLEAN NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX ix_roles_id ON roles (id)")
            cursor.execute("CREATE INDEX ix_roles_name ON roles (name)")
            cursor.execute("CREATE INDEX ix_roles_slug ON roles (slug)")
            print("✓ Roles table created successfully")

        # Step 2: Create default system roles
        print("\nCreating default system roles...")

        # Check if superadmin role exists
        cursor.execute("SELECT id FROM roles WHERE slug = 'superadmin'")
        superadmin_role = cursor.fetchone()

        if not superadmin_role:
            cursor.execute("""
                INSERT INTO roles (name, slug, description, is_system_role)
                VALUES ('Super Admin', 'superadmin', 'Full system access with all permissions', 1)
            """)
            superadmin_id = cursor.lastrowid
            print(f"✓ Created 'Super Admin' role (ID: {superadmin_id})")
        else:
            superadmin_id = superadmin_role[0]
            print(f"✓ 'Super Admin' role already exists (ID: {superadmin_id})")

        # Check if writer role exists
        cursor.execute("SELECT id FROM roles WHERE slug = 'writer'")
        writer_role = cursor.fetchone()

        if not writer_role:
            cursor.execute("""
                INSERT INTO roles (name, slug, description, is_system_role)
                VALUES ('Writer', 'writer', 'Can create and manage content', 1)
            """)
            writer_id = cursor.lastrowid
            print(f"✓ Created 'Writer' role (ID: {writer_id})")
        else:
            writer_id = writer_role[0]
            print(f"✓ 'Writer' role already exists (ID: {writer_id})")

        # Step 3: Check if admins table has role_id column
        cursor.execute("PRAGMA table_info(admins)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'role_id' in columns:
            print("\n✓ Admins table already has role_id column")
        else:
            print("\nMigrating admins table...")

            # Add role_id column (nullable first)
            cursor.execute("ALTER TABLE admins ADD COLUMN role_id INTEGER")
            print("✓ Added role_id column to admins table")

            # Migrate existing admin records
            cursor.execute("SELECT id, role FROM admins WHERE role_id IS NULL")
            admins_to_migrate = cursor.fetchall()

            if admins_to_migrate:
                print(f"\nMigrating {len(admins_to_migrate)} admin(s)...")

                for admin_id, old_role in admins_to_migrate:
                    if old_role == "superadmin":
                        new_role_id = superadmin_id
                        role_name = "Super Admin"
                    else:
                        new_role_id = writer_id
                        role_name = "Writer"

                    cursor.execute("""
                        UPDATE admins
                        SET role_id = ?
                        WHERE id = ?
                    """, (new_role_id, admin_id))

                    print(f"  ✓ Migrated admin ID {admin_id}: '{old_role}' → '{role_name}' (role_id: {new_role_id})")

                print(f"✓ Successfully migrated {len(admins_to_migrate)} admin(s)")
            else:
                print("✓ No admins to migrate")

            # Step 4: Drop old role column
            print("\nUpdating table schema...")

            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            cursor.execute("""
                CREATE TABLE admins_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR NOT NULL UNIQUE,
                    hashed_password VARCHAR NOT NULL,
                    role_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (role_id) REFERENCES roles (id)
                )
            """)

            cursor.execute("""
                INSERT INTO admins_new (id, username, hashed_password, role_id, created_at)
                SELECT id, username, hashed_password, role_id, created_at
                FROM admins
            """)

            cursor.execute("DROP TABLE admins")
            cursor.execute("ALTER TABLE admins_new RENAME TO admins")

            # Recreate indexes
            cursor.execute("CREATE INDEX ix_admins_id ON admins (id)")
            cursor.execute("CREATE INDEX ix_admins_username ON admins (username)")

            print("✓ Updated admins table schema (removed old role column)")

        # Commit all changes
        conn.commit()

        # Step 5: Verification
        print("\n" + "-" * 50)
        print("Verification:")
        print("-" * 50)

        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]
        print(f"Total roles in system: {role_count}")

        cursor.execute("SELECT COUNT(*) FROM admins")
        admin_count = cursor.fetchone()[0]
        print(f"Total admins in system: {admin_count}")

        cursor.execute("""
            SELECT r.name, COUNT(a.id) as admin_count
            FROM roles r
            LEFT JOIN admins a ON r.id = a.role_id
            GROUP BY r.id, r.name
            ORDER BY r.is_system_role DESC, r.name
        """)

        print("\nRole distribution:")
        for role_name, count in cursor.fetchall():
            print(f"  - {role_name}: {count} admin(s)")

        print("\n" + "=" * 50)
        print("✓ Migration completed successfully!")
        print("=" * 50)
        print("\nYou can now:")
        print("1. Create custom roles via the API (/api/roles)")
        print("2. Assign roles to admins via admin management (/api/admin)")
        print("3. Delete the old migrate_add_role.py file (no longer needed)")

    except sqlite3.Error as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        print("\nRolling back changes...")
    finally:
        conn.close()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Role System Migration Tool                         ║
║          Bocah Cafe API v2.0                                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    response = input("This will upgrade your database to use the new role system.\nContinue? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        migrate_to_role_system()
    else:
        print("Migration cancelled.")
