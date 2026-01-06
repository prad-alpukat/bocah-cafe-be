"""
Migration: Convert Facility Icons to Iconify Format

This migration converts existing facility icons from simple string names
to the new Iconify format (iconify:set:name).

Run this migration manually:
    python migrations/migrate_facility_icons.py

Options:
    --dry-run    Preview changes without applying them
    --rollback   Revert to original icon names (if backup exists)
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Facility

# Icon mapping: old_name -> iconify format
ICON_MAPPING = {
    # Common facility icons
    "wifi": "iconify:lucide:wifi",
    "ac": "iconify:lucide:snowflake",
    "snowflake": "iconify:lucide:snowflake",
    "mushola": "iconify:lucide:church",
    "mosque": "iconify:mdi:mosque",
    "toilet": "iconify:lucide:bath",
    "restroom": "iconify:lucide:bath",
    "parking": "iconify:lucide:car",
    "car-parking": "iconify:lucide:car",
    "car": "iconify:lucide:car",
    "motorcycle": "iconify:lucide:bike",
    "outdoor": "iconify:lucide:trees",
    "tree": "iconify:lucide:tree-pine",
    "indoor": "iconify:lucide:home",
    "smoking-area": "iconify:lucide:cigarette",
    "smoking": "iconify:lucide:cigarette",
    "smoking-ban": "iconify:lucide:cigarette-off",
    "meeting-room": "iconify:lucide:users",
    "power-outlet": "iconify:lucide:plug",
    "plug": "iconify:lucide:plug",
    "pet-friendly": "iconify:lucide:paw-print",
    "paw": "iconify:lucide:paw-print",
    "live-music": "iconify:lucide:music",
    "music": "iconify:lucide:music",
    "board-games": "iconify:lucide:dice-5",
    "door-closed": "iconify:lucide:door-closed",
    "calendar-check": "iconify:lucide:calendar-check",

    # Additional common icons
    "coffee": "iconify:lucide:coffee",
    "food": "iconify:lucide:utensils",
    "wheelchair": "iconify:lucide:accessibility",
    "tv": "iconify:lucide:tv",
    "projector": "iconify:lucide:projector",
    "printer": "iconify:lucide:printer",
    "clock": "iconify:lucide:clock",
    "24h": "iconify:lucide:clock",
    "credit-card": "iconify:lucide:credit-card",
    "cash": "iconify:lucide:banknote",

    # E-commerce & delivery
    "shopping-bag": "iconify:lucide:shopping-bag",
    "truck": "iconify:lucide:truck",
    "delivery": "iconify:lucide:truck",
    "take-away": "iconify:lucide:shopping-bag",

    # Payment
    "qrcode": "iconify:lucide:qr-code",
    "qris": "iconify:lucide:qr-code",

    # Family
    "child": "iconify:lucide:baby",
    "kids-area": "iconify:lucide:baby",
}

# Backup file path
BACKUP_FILE = "migrations/facility_icons_backup.json"


def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def backup_icons(db: Session) -> dict:
    """Backup current icon values before migration"""
    facilities = db.query(Facility).all()
    backup = {
        "timestamp": datetime.utcnow().isoformat(),
        "icons": {f.id: {"slug": f.slug, "icon": f.icon} for f in facilities}
    }
    return backup


def save_backup(backup: dict):
    """Save backup to file"""
    with open(BACKUP_FILE, 'w') as f:
        json.dump(backup, f, indent=2)
    print(f"Backup saved to {BACKUP_FILE}")


def load_backup() -> dict:
    """Load backup from file"""
    if not os.path.exists(BACKUP_FILE):
        raise FileNotFoundError(f"Backup file not found: {BACKUP_FILE}")
    with open(BACKUP_FILE, 'r') as f:
        return json.load(f)


def migrate_icons(db: Session, dry_run: bool = False) -> dict:
    """
    Migrate facility icons to Iconify format.

    Returns:
        dict with migration statistics
    """
    facilities = db.query(Facility).all()

    stats = {
        "total": len(facilities),
        "migrated": 0,
        "skipped": 0,
        "already_iconify": 0,
        "already_url": 0,
        "no_icon": 0,
        "unmapped": [],
        "changes": []
    }

    for facility in facilities:
        old_icon = facility.icon

        # Skip if no icon
        if not old_icon or old_icon.strip() == "":
            stats["no_icon"] += 1
            continue

        old_icon = old_icon.strip()

        # Skip if already in Iconify format
        if old_icon.startswith("iconify:"):
            stats["already_iconify"] += 1
            continue

        # Skip if already a URL
        if old_icon.startswith("http://") or old_icon.startswith("https://"):
            stats["already_url"] += 1
            continue

        # Try to find mapping
        new_icon = ICON_MAPPING.get(old_icon.lower())

        if new_icon:
            stats["changes"].append({
                "facility_id": facility.id,
                "slug": facility.slug,
                "old_icon": old_icon,
                "new_icon": new_icon
            })

            if not dry_run:
                facility.icon = new_icon

            stats["migrated"] += 1
        else:
            stats["unmapped"].append({
                "facility_id": facility.id,
                "slug": facility.slug,
                "icon": old_icon
            })
            stats["skipped"] += 1

    if not dry_run:
        db.commit()

    return stats


def rollback_icons(db: Session) -> dict:
    """
    Rollback icons to original values from backup.

    Returns:
        dict with rollback statistics
    """
    backup = load_backup()

    stats = {
        "total": 0,
        "restored": 0,
        "not_found": 0,
        "unchanged": 0
    }

    for facility_id, data in backup["icons"].items():
        stats["total"] += 1

        facility = db.query(Facility).filter(Facility.id == facility_id).first()

        if not facility:
            stats["not_found"] += 1
            continue

        if facility.icon == data["icon"]:
            stats["unchanged"] += 1
            continue

        facility.icon = data["icon"]
        stats["restored"] += 1

    db.commit()
    return stats


def print_stats(stats: dict, action: str = "migration"):
    """Pretty print migration/rollback statistics"""
    print("\n" + "=" * 50)
    print(f"  Facility Icon {action.title()} Report")
    print("=" * 50)

    if action == "migration":
        print(f"\nTotal facilities: {stats['total']}")
        print(f"  - Migrated:        {stats['migrated']}")
        print(f"  - Already Iconify: {stats['already_iconify']}")
        print(f"  - Already URL:     {stats['already_url']}")
        print(f"  - No icon:         {stats['no_icon']}")
        print(f"  - Skipped (unmapped): {stats['skipped']}")

        if stats["changes"]:
            print("\nChanges:")
            for change in stats["changes"]:
                print(f"  [{change['slug']}] {change['old_icon']} -> {change['new_icon']}")

        if stats["unmapped"]:
            print("\nUnmapped icons (need manual update):")
            for item in stats["unmapped"]:
                print(f"  [{item['slug']}] {item['icon']}")
                print(f"    Add to ICON_MAPPING: \"{item['icon'].lower()}\": \"iconify:lucide:???\"")

    elif action == "rollback":
        print(f"\nTotal in backup: {stats['total']}")
        print(f"  - Restored:   {stats['restored']}")
        print(f"  - Not found:  {stats['not_found']}")
        print(f"  - Unchanged:  {stats['unchanged']}")

    print("\n" + "=" * 50)


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    rollback = "--rollback" in args

    print("\nFacility Icon Migration Tool")
    print("-" * 30)

    db = get_db()

    try:
        if rollback:
            print("Mode: ROLLBACK")
            print("Restoring icons from backup...")
            stats = rollback_icons(db)
            print_stats(stats, "rollback")
            print("\nRollback completed!")

        else:
            mode = "DRY RUN (preview only)" if dry_run else "LIVE"
            print(f"Mode: {mode}")

            if not dry_run:
                # Create backup before migration
                print("Creating backup...")
                backup = backup_icons(db)
                save_backup(backup)

            print("Migrating icons...")
            stats = migrate_icons(db, dry_run=dry_run)
            print_stats(stats, "migration")

            if dry_run:
                print("\nThis was a dry run. No changes were made.")
                print("Run without --dry-run to apply changes.")
            else:
                print("\nMigration completed!")
                print(f"Backup saved to: {BACKUP_FILE}")
                print("To rollback: python migrations/migrate_facility_icons.py --rollback")

    finally:
        db.close()


if __name__ == "__main__":
    main()
