#!/usr/bin/env python3
"""
Database Seeder Runner for Bocah Cafe API
==========================================

Usage:
    python seed.py              # Run all seeders
    python seed.py --fresh      # Drop all tables and re-seed
    python seed.py --only roles # Run specific seeder only
    python seed.py --help       # Show help

Available seeders:
    - roles       : System roles (superadmin, admin, writer, viewer)
    - admins      : Default admin user (admin/password)
    - facilities  : Cafe facilities (wifi, mushola, ac, etc.)
    - cafes       : Sample cafe data (100 cafes)
    - collections : Sample collections (public, private, password protected)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database import engine, Base, SessionLocal
from seeders import RoleSeeder, AdminSeeder, FacilitySeeder, CafeSeeder, CollectionSeeder


# Seeder registry - order matters!
SEEDERS = [
    ("roles", RoleSeeder),
    ("admins", AdminSeeder),
    ("facilities", FacilitySeeder),
    ("cafes", CafeSeeder),
    ("collections", CollectionSeeder),
]


def print_banner():
    """Print application banner"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║              Bocah Cafe API - Database Seeder             ║
╚═══════════════════════════════════════════════════════════╝
    """)


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created\n")


def drop_tables():
    """Drop all database tables"""
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped\n")


def run_seeders(only: str = None):
    """Run seeders"""
    db = SessionLocal()

    try:
        for name, seeder_class in SEEDERS:
            # Skip if --only is specified and doesn't match
            if only and name != only:
                continue

            seeder = seeder_class(db)
            print(f"[{seeder.name}]")
            print("-" * 40)

            try:
                seeder.run()
                print(f"✓ {seeder.name} seeder completed\n")
            except Exception as e:
                print(f"✗ {seeder.name} seeder failed: {e}\n")
                db.rollback()
                raise

    finally:
        db.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Database seeder for Bocah Cafe API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seed.py                    Run all seeders
  python seed.py --fresh            Reset database and run all seeders
  python seed.py --only roles       Run only roles seeder
  python seed.py --only facilities  Run only facilities seeder
        """
    )

    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Drop all tables before seeding (WARNING: destroys all data)"
    )

    parser.add_argument(
        "--only",
        type=str,
        choices=[name for name, _ in SEEDERS],
        help="Run only a specific seeder"
    )

    args = parser.parse_args()

    print_banner()

    # Confirm fresh if specified
    if args.fresh:
        print("⚠  WARNING: --fresh will delete ALL existing data!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Aborted.")
            sys.exit(0)
        print()
        drop_tables()

    # Create tables
    create_tables()

    # Run seeders
    print("Running seeders...")
    print("=" * 50)
    run_seeders(only=args.only)

    print("=" * 50)
    print("✓ Seeding completed successfully!")
    print()
    print("Default admin credentials:")
    print("  Username: admin")
    print("  Password: password")
    print()


if __name__ == "__main__":
    main()
