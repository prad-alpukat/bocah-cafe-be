"""
Migration script to add role column to admins table
Run this once to update the database schema
"""
import sqlite3
from pathlib import Path

def migrate_add_role():
    db_path = Path(__file__).parent / "bocah_cafe.db"

    if not db_path.exists():
        print("Database file not found. Creating tables will include role column.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if role column already exists
        cursor.execute("PRAGMA table_info(admins)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'role' in columns:
            print("✓ Role column already exists. No migration needed.")
            return

        # Add role column with default value
        print("Adding role column to admins table...")
        cursor.execute("""
            ALTER TABLE admins
            ADD COLUMN role TEXT NOT NULL DEFAULT 'writer'
        """)

        # Update existing admins to have writer role (or you can set first admin as superadmin)
        cursor.execute("SELECT COUNT(*) FROM admins")
        admin_count = cursor.fetchone()[0]

        if admin_count > 0:
            # Optionally, set the first admin as superadmin
            cursor.execute("""
                UPDATE admins
                SET role = 'superadmin'
                WHERE id = (SELECT MIN(id) FROM admins)
            """)
            print(f"✓ First admin set as superadmin, remaining {admin_count - 1} admins set as writer")

        conn.commit()
        print("✓ Migration completed successfully!")

    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_add_role()
