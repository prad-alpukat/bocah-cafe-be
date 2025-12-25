"""
Migration script untuk menambahkan tabel collections dan collection_cafes
ke database yang sudah ada.

Jalankan script ini setelah update kode untuk membuat tabel baru.
"""

from sqlalchemy import inspect
from database import engine, Base
from models import Collection, collection_cafes

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate():
    print("=" * 50)
    print("Migration: Add Collections Feature")
    print("=" * 50)

    # Check existing tables
    collections_exists = check_table_exists('collections')
    collection_cafes_exists = check_table_exists('collection_cafes')

    if collections_exists and collection_cafes_exists:
        print("\n✓ Tables 'collections' and 'collection_cafes' already exist.")
        print("  Migration not needed.")
        return

    print("\nCreating new tables...")

    # Create only the new tables
    tables_to_create = []

    if not collection_cafes_exists:
        tables_to_create.append(collection_cafes)
        print("  - collection_cafes (association table)")

    if not collections_exists:
        tables_to_create.append(Collection.__table__)
        print("  - collections")

    # Create tables
    for table in tables_to_create:
        table.create(engine, checkfirst=True)

    print("\n✓ Migration completed successfully!")
    print("\nNew tables created:")
    print("  - collections: Stores collection metadata")
    print("  - collection_cafes: Many-to-many relationship between collections and cafes")

    print("\n" + "=" * 50)
    print("You can now use the Collection API endpoints:")
    print("  GET    /api/collections          - List public collections")
    print("  GET    /api/collections/{id}     - Get collection by ID")
    print("  GET    /api/collections/slug/{s} - Get collection by slug")
    print("  POST   /api/collections/{id}/access - Access password-protected collection")
    print("")
    print("Admin endpoints (requires authentication):")
    print("  GET    /api/collections/admin/all     - List all collections")
    print("  POST   /api/collections               - Create collection")
    print("  PUT    /api/collections/{id}          - Update collection")
    print("  DELETE /api/collections/{id}          - Delete collection")
    print("  POST   /api/collections/{id}/cafes    - Add cafes to collection")
    print("  DELETE /api/collections/{id}/cafes    - Remove cafes from collection")
    print("=" * 50)

if __name__ == "__main__":
    migrate()
