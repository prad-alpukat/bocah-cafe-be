"""
Migration: Add Full-Text Search Index for MySQL

This migration adds FULLTEXT indexes to improve search performance on MySQL.
For SQLite (development), this migration will be skipped.

Run this migration manually after deploying to production:
    python migrations/add_fulltext_index.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine
from config import settings


def run_migration():
    """Add FULLTEXT indexes for MySQL"""

    # Check if using MySQL
    is_mysql = "mysql" in settings.DATABASE_URL.lower()

    if not is_mysql:
        print("Skipping FULLTEXT index migration - not using MySQL")
        print("Current DATABASE_URL uses:", settings.DATABASE_URL.split(":")[0])
        return

    print("Running FULLTEXT index migration for MySQL...")

    with engine.connect() as conn:
        # Check and create FULLTEXT index on cafes table
        try:
            # Drop existing index if any
            conn.execute(text("DROP INDEX IF EXISTS idx_cafe_fulltext ON cafes"))
        except Exception:
            pass

        try:
            conn.execute(text("""
                CREATE FULLTEXT INDEX idx_cafe_fulltext
                ON cafes(nama, alamat_lengkap)
            """))
            print("Created FULLTEXT index on cafes(nama, alamat_lengkap)")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                print("FULLTEXT index on cafes already exists")
            else:
                print(f"Error creating cafes index: {e}")

        # FULLTEXT index on facilities
        try:
            conn.execute(text("DROP INDEX IF EXISTS idx_facility_fulltext ON facilities"))
        except Exception:
            pass

        try:
            conn.execute(text("""
                CREATE FULLTEXT INDEX idx_facility_fulltext
                ON facilities(name, description)
            """))
            print("Created FULLTEXT index on facilities(name, description)")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                print("FULLTEXT index on facilities already exists")
            else:
                print(f"Error creating facilities index: {e}")

        # FULLTEXT index on collections
        try:
            conn.execute(text("DROP INDEX IF EXISTS idx_collection_fulltext ON collections"))
        except Exception:
            pass

        try:
            conn.execute(text("""
                CREATE FULLTEXT INDEX idx_collection_fulltext
                ON collections(name, description)
            """))
            print("Created FULLTEXT index on collections(name, description)")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                print("FULLTEXT index on collections already exists")
            else:
                print(f"Error creating collections index: {e}")

        conn.commit()
        print("Migration completed!")


def rollback_migration():
    """Remove FULLTEXT indexes"""
    is_mysql = "mysql" in settings.DATABASE_URL.lower()

    if not is_mysql:
        print("Skipping rollback - not using MySQL")
        return

    print("Rolling back FULLTEXT indexes...")

    with engine.connect() as conn:
        try:
            conn.execute(text("DROP INDEX idx_cafe_fulltext ON cafes"))
            print("Dropped idx_cafe_fulltext")
        except Exception as e:
            print(f"Could not drop idx_cafe_fulltext: {e}")

        try:
            conn.execute(text("DROP INDEX idx_facility_fulltext ON facilities"))
            print("Dropped idx_facility_fulltext")
        except Exception as e:
            print(f"Could not drop idx_facility_fulltext: {e}")

        try:
            conn.execute(text("DROP INDEX idx_collection_fulltext ON collections"))
            print("Dropped idx_collection_fulltext")
        except Exception as e:
            print(f"Could not drop idx_collection_fulltext: {e}")

        conn.commit()
        print("Rollback completed!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FULLTEXT index migration")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    args = parser.parse_args()

    if args.rollback:
        rollback_migration()
    else:
        run_migration()
