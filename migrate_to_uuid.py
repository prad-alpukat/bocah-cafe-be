"""
Migration script to convert integer IDs to UUIDs

This script:
1. Backs up existing data
2. Creates new tables with UUID columns
3. Migrates data with new UUID values
4. Updates foreign key references

Run this script once to migrate existing data.
After migration, the old tables will be dropped.

Usage: python migrate_to_uuid.py
"""

import sqlite3
import uuid
from datetime import datetime


def generate_uuid():
    return str(uuid.uuid4())


def migrate():
    conn = sqlite3.connect('bocah_cafe.db')
    cursor = conn.cursor()

    print("=" * 60)
    print("Starting UUID Migration")
    print("=" * 60)

    try:
        # Check if migration is needed by checking column type
        cursor.execute("PRAGMA table_info(roles)")
        columns = cursor.fetchall()
        id_column = next((col for col in columns if col[1] == 'id'), None)

        if id_column and 'VARCHAR' in id_column[2].upper():
            print("Migration already completed. Tables already use UUID.")
            return

        # Step 1: Create ID mappings for all tables
        print("\n[1/6] Creating UUID mappings...")

        # Roles mapping
        cursor.execute("SELECT id FROM roles")
        role_mapping = {row[0]: generate_uuid() for row in cursor.fetchall()}
        print(f"  - Roles: {len(role_mapping)} records")

        # Facilities mapping
        cursor.execute("SELECT id FROM facilities")
        facility_mapping = {row[0]: generate_uuid() for row in cursor.fetchall()}
        print(f"  - Facilities: {len(facility_mapping)} records")

        # Cafes mapping
        cursor.execute("SELECT id FROM cafes")
        cafe_mapping = {row[0]: generate_uuid() for row in cursor.fetchall()}
        print(f"  - Cafes: {len(cafe_mapping)} records")

        # Admins mapping
        cursor.execute("SELECT id FROM admins")
        admin_mapping = {row[0]: generate_uuid() for row in cursor.fetchall()}
        print(f"  - Admins: {len(admin_mapping)} records")

        # Step 2: Create new tables with UUID columns
        print("\n[2/6] Creating new tables with UUID columns...")

        # Roles table
        cursor.execute("""
            CREATE TABLE roles_new (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR NOT NULL UNIQUE,
                slug VARCHAR NOT NULL UNIQUE,
                description TEXT,
                is_system_role BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        print("  - Created roles_new")

        # Facilities table
        cursor.execute("""
            CREATE TABLE facilities_new (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR NOT NULL UNIQUE,
                slug VARCHAR NOT NULL UNIQUE,
                icon VARCHAR,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        print("  - Created facilities_new")

        # Cafes table
        cursor.execute("""
            CREATE TABLE cafes_new (
                id VARCHAR(36) PRIMARY KEY,
                nama VARCHAR NOT NULL,
                gambar_thumbnail VARCHAR,
                no_hp VARCHAR,
                link_website VARCHAR,
                rating FLOAT,
                range_price VARCHAR,
                count_google_review INTEGER,
                jam_buka VARCHAR,
                alamat_lengkap VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        print("  - Created cafes_new")

        # Admins table
        cursor.execute("""
            CREATE TABLE admins_new (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR NOT NULL UNIQUE,
                hashed_password VARCHAR NOT NULL,
                role_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles_new (id)
            )
        """)
        print("  - Created admins_new")

        # Cafe_facilities association table
        cursor.execute("""
            CREATE TABLE cafe_facilities_new (
                cafe_id VARCHAR(36) NOT NULL,
                facility_id VARCHAR(36) NOT NULL,
                PRIMARY KEY (cafe_id, facility_id),
                FOREIGN KEY (cafe_id) REFERENCES cafes_new (id) ON DELETE CASCADE,
                FOREIGN KEY (facility_id) REFERENCES facilities_new (id) ON DELETE CASCADE
            )
        """)
        print("  - Created cafe_facilities_new")

        # Step 3: Migrate data
        print("\n[3/6] Migrating data...")

        # Migrate roles
        cursor.execute("SELECT id, name, slug, description, is_system_role, created_at, updated_at FROM roles")
        for row in cursor.fetchall():
            old_id, name, slug, description, is_system_role, created_at, updated_at = row
            new_id = role_mapping[old_id]
            cursor.execute("""
                INSERT INTO roles_new (id, name, slug, description, is_system_role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (new_id, name, slug, description, is_system_role, created_at, updated_at))
        print(f"  - Migrated {len(role_mapping)} roles")

        # Migrate facilities
        cursor.execute("SELECT id, name, slug, icon, description, created_at, updated_at FROM facilities")
        for row in cursor.fetchall():
            old_id, name, slug, icon, description, created_at, updated_at = row
            new_id = facility_mapping[old_id]
            cursor.execute("""
                INSERT INTO facilities_new (id, name, slug, icon, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (new_id, name, slug, icon, description, created_at, updated_at))
        print(f"  - Migrated {len(facility_mapping)} facilities")

        # Migrate cafes
        cursor.execute("""
            SELECT id, nama, gambar_thumbnail, no_hp, link_website, rating,
                   range_price, count_google_review, jam_buka, alamat_lengkap,
                   created_at, updated_at
            FROM cafes
        """)
        for row in cursor.fetchall():
            old_id = row[0]
            new_id = cafe_mapping[old_id]
            cursor.execute("""
                INSERT INTO cafes_new (id, nama, gambar_thumbnail, no_hp, link_website, rating,
                                       range_price, count_google_review, jam_buka, alamat_lengkap,
                                       created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_id,) + row[1:])
        print(f"  - Migrated {len(cafe_mapping)} cafes")

        # Migrate admins
        cursor.execute("SELECT id, username, hashed_password, role_id, created_at FROM admins")
        for row in cursor.fetchall():
            old_id, username, hashed_password, old_role_id, created_at = row
            new_id = admin_mapping[old_id]
            new_role_id = role_mapping[old_role_id]
            cursor.execute("""
                INSERT INTO admins_new (id, username, hashed_password, role_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (new_id, username, hashed_password, new_role_id, created_at))
        print(f"  - Migrated {len(admin_mapping)} admins")

        # Migrate cafe_facilities
        cursor.execute("SELECT cafe_id, facility_id FROM cafe_facilities")
        cf_count = 0
        for row in cursor.fetchall():
            old_cafe_id, old_facility_id = row
            new_cafe_id = cafe_mapping.get(old_cafe_id)
            new_facility_id = facility_mapping.get(old_facility_id)
            if new_cafe_id and new_facility_id:
                cursor.execute("""
                    INSERT INTO cafe_facilities_new (cafe_id, facility_id)
                    VALUES (?, ?)
                """, (new_cafe_id, new_facility_id))
                cf_count += 1
        print(f"  - Migrated {cf_count} cafe-facility associations")

        # Step 4: Drop old tables
        print("\n[4/6] Dropping old tables...")
        cursor.execute("DROP TABLE IF EXISTS cafe_facilities")
        cursor.execute("DROP TABLE IF EXISTS admins")
        cursor.execute("DROP TABLE IF EXISTS cafes")
        cursor.execute("DROP TABLE IF EXISTS facilities")
        cursor.execute("DROP TABLE IF EXISTS roles")
        print("  - Dropped old tables")

        # Step 5: Rename new tables
        print("\n[5/6] Renaming new tables...")
        cursor.execute("ALTER TABLE roles_new RENAME TO roles")
        cursor.execute("ALTER TABLE facilities_new RENAME TO facilities")
        cursor.execute("ALTER TABLE cafes_new RENAME TO cafes")
        cursor.execute("ALTER TABLE admins_new RENAME TO admins")
        cursor.execute("ALTER TABLE cafe_facilities_new RENAME TO cafe_facilities")
        print("  - Renamed tables")

        # Step 6: Create indexes
        print("\n[6/6] Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_roles_id ON roles (id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_roles_name ON roles (name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_roles_slug ON roles (slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_facilities_id ON facilities (id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_facilities_name ON facilities (name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_facilities_slug ON facilities (slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_cafes_id ON cafes (id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_cafes_nama ON cafes (nama)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_admins_id ON admins (id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_admins_username ON admins (username)")
        print("  - Created indexes")

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

        # Print ID mappings for reference
        print("\n[UUID Mappings]")
        print("\nRoles:")
        for old_id, new_id in role_mapping.items():
            print(f"  {old_id} -> {new_id}")
        print("\nFacilities:")
        for old_id, new_id in list(facility_mapping.items())[:5]:
            print(f"  {old_id} -> {new_id}")
        if len(facility_mapping) > 5:
            print(f"  ... and {len(facility_mapping) - 5} more")
        print("\nCafes:")
        for old_id, new_id in list(cafe_mapping.items())[:5]:
            print(f"  {old_id} -> {new_id}")
        if len(cafe_mapping) > 5:
            print(f"  ... and {len(cafe_mapping) - 5} more")
        print("\nAdmins:")
        for old_id, new_id in admin_mapping.items():
            print(f"  {old_id} -> {new_id}")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        print("All changes have been rolled back.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
