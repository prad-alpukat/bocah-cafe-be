"""
Collection seeder - Creates sample collection data for development/testing
"""
from sqlalchemy.orm import Session
from models import Collection, Cafe
from auth_utils import get_password_hash
from .base_seeder import BaseSeeder


class CollectionSeeder(BaseSeeder):
    """Seeder for sample collection data"""

    @property
    def name(self) -> str:
        return "Collections"

    # Sample collections data
    COLLECTIONS = [
        # Public Collections
        {
            "name": "Best for WFH",
            "slug": "best-for-wfh",
            "description": "Cafe-cafe terbaik untuk Work From Home dengan WiFi kencang, colokan listrik, dan suasana nyaman untuk produktif.",
            "gambar_cover": "https://example.com/covers/wfh.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "must_have_facilities": ["wifi", "power-outlet", "ac"],
                "min_rating": 4.3
            }
        },
        {
            "name": "Pet-Friendly Cafes",
            "slug": "pet-friendly-cafes",
            "description": "Kumpulan cafe yang ramah hewan peliharaan. Bawa anjing atau kucing kesayanganmu!",
            "gambar_cover": "https://example.com/covers/pet-friendly.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "must_have_facilities": ["pet-friendly"]
            }
        },
        {
            "name": "Romantic Date Spots",
            "slug": "romantic-date-spots",
            "description": "Cafe-cafe dengan suasana romantis untuk kencan spesial bersama pasangan.",
            "gambar_cover": "https://example.com/covers/romantic.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "must_have_facilities": ["outdoor"],
                "min_rating": 4.5
            }
        },
        {
            "name": "Budget Friendly",
            "slug": "budget-friendly",
            "description": "Cafe-cafe dengan harga terjangkau tapi tetap enak dan nyaman.",
            "gambar_cover": "https://example.com/covers/budget.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "max_price_keyword": "15.000"
            }
        },
        {
            "name": "Live Music Venues",
            "slug": "live-music-venues",
            "description": "Cafe dengan live music untuk menikmati kopi sambil mendengarkan musik live.",
            "gambar_cover": "https://example.com/covers/live-music.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "must_have_facilities": ["live-music"]
            }
        },
        {
            "name": "Family Friendly",
            "slug": "family-friendly",
            "description": "Cafe yang cocok untuk keluarga dengan area bermain anak.",
            "gambar_cover": "https://example.com/covers/family.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "must_have_facilities": ["kids-area"]
            }
        },
        {
            "name": "Premium Coffee Experience",
            "slug": "premium-coffee-experience",
            "description": "Cafe-cafe premium dengan kopi specialty dan pengalaman terbaik.",
            "gambar_cover": "https://example.com/covers/premium.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "min_rating": 4.6,
                "min_reviews": 1000
            }
        },
        {
            "name": "Hidden Gems Jakarta",
            "slug": "hidden-gems-jakarta",
            "description": "Cafe-cafe tersembunyi di Jakarta yang wajib dicoba.",
            "gambar_cover": "https://example.com/covers/hidden-gems.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "max_reviews": 500,
                "min_rating": 4.4
            }
        },
        {
            "name": "24 Hour Cafes",
            "slug": "24-hour-cafes",
            "description": "Cafe yang buka 24 jam untuk yang suka begadang.",
            "gambar_cover": "https://example.com/covers/24hours.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "open_late": True
            }
        },
        {
            "name": "Instagrammable Spots",
            "slug": "instagrammable-spots",
            "description": "Cafe-cafe dengan spot foto aesthetic untuk feed Instagram kamu.",
            "gambar_cover": "https://example.com/covers/instagram.jpg",
            "visibility": "public",
            "password": None,
            "cafe_filters": {
                "must_have_facilities": ["outdoor"],
                "min_rating": 4.4
            }
        },
        # Private Collections (Admin Only)
        {
            "name": "Staff Favorites",
            "slug": "staff-favorites",
            "description": "Koleksi cafe favorit tim Bocah Cafe. Internal only.",
            "gambar_cover": "https://example.com/covers/staff.jpg",
            "visibility": "private",
            "password": None,
            "cafe_filters": {
                "min_rating": 4.5
            }
        },
        {
            "name": "Upcoming Partners",
            "slug": "upcoming-partners",
            "description": "Cafe-cafe yang sedang dalam proses partnership. Confidential.",
            "gambar_cover": "https://example.com/covers/partners.jpg",
            "visibility": "private",
            "password": None,
            "cafe_filters": {
                "random": 5
            }
        },
        # Password Protected Collections
        {
            "name": "VIP Member Collection",
            "slug": "vip-member-collection",
            "description": "Koleksi eksklusif untuk member VIP dengan diskon dan promo spesial.",
            "gambar_cover": "https://example.com/covers/vip.jpg",
            "visibility": "password_protected",
            "password": "vip2024",
            "cafe_filters": {
                "min_rating": 4.6,
                "must_have_facilities": ["reservation", "private-room"]
            }
        },
        {
            "name": "Corporate Deals",
            "slug": "corporate-deals",
            "description": "Cafe dengan penawaran khusus untuk corporate event dan meeting.",
            "gambar_cover": "https://example.com/covers/corporate.jpg",
            "visibility": "password_protected",
            "password": "corporate123",
            "cafe_filters": {
                "must_have_facilities": ["private-room", "wifi"]
            }
        },
        {
            "name": "Beta Tester Picks",
            "slug": "beta-tester-picks",
            "description": "Rekomendasi dari beta tester Bocah Cafe App.",
            "gambar_cover": "https://example.com/covers/beta.jpg",
            "visibility": "password_protected",
            "password": "beta2024",
            "cafe_filters": {
                "random": 10
            }
        }
    ]

    def _filter_cafes(self, filters: dict) -> list:
        """Filter cafes based on criteria"""
        from models import Facility

        query = self.db.query(Cafe)

        # Filter by facilities
        if "must_have_facilities" in filters:
            facility_slugs = filters["must_have_facilities"]
            for slug in facility_slugs:
                facility = self.db.query(Facility).filter(Facility.slug == slug).first()
                if facility:
                    query = query.filter(Cafe.facilities.contains(facility))

        # Filter by minimum rating
        if "min_rating" in filters:
            query = query.filter(Cafe.rating >= filters["min_rating"])

        # Filter by minimum reviews
        if "min_reviews" in filters:
            query = query.filter(Cafe.count_google_review >= filters["min_reviews"])

        # Filter by maximum reviews (for hidden gems)
        if "max_reviews" in filters:
            query = query.filter(Cafe.count_google_review <= filters["max_reviews"])

        # Filter by price keyword
        if "max_price_keyword" in filters:
            keyword = filters["max_price_keyword"]
            query = query.filter(Cafe.range_price.ilike(f"%{keyword}%"))

        # Filter by late hours
        if filters.get("open_late"):
            query = query.filter(
                (Cafe.jam_buka.ilike("%23:00%")) |
                (Cafe.jam_buka.ilike("%24:00%")) |
                (Cafe.jam_buka.ilike("%00:00%"))
            )

        # Get results
        cafes = query.all()

        # Random selection if specified
        if "random" in filters:
            import random
            count = min(filters["random"], len(cafes))
            cafes = random.sample(cafes, count) if cafes else []

        # Limit to max 15 cafes per collection
        return cafes[:15]

    def run(self) -> None:
        """Create sample collections if they don't exist"""
        # Check if we have cafes
        cafe_count = self.db.query(Cafe).count()
        if cafe_count == 0:
            self.log("No cafes found. Run CafeSeeder first.", "warning")
            return

        self.log(f"Found {cafe_count} cafes in database")

        created_count = 0
        skipped_count = 0

        for collection_data in self.COLLECTIONS:
            # Check if collection already exists
            existing = self.db.query(Collection).filter(
                Collection.slug == collection_data["slug"]
            ).first()

            if existing:
                self.log(f"Collection '{collection_data['name']}' already exists (ID: {existing.id})", "skip")
                skipped_count += 1
                continue

            # Extract filters and password
            cafe_filters = collection_data.pop("cafe_filters", {})
            password = collection_data.pop("password", None)

            # Hash password if provided
            password_hash = None
            if password and collection_data["visibility"] == "password_protected":
                password_hash = get_password_hash(password)

            # Create collection
            collection = Collection(
                name=collection_data["name"],
                slug=collection_data["slug"],
                description=collection_data["description"],
                gambar_cover=collection_data["gambar_cover"],
                visibility=collection_data["visibility"],
                password_hash=password_hash
            )

            # Add filtered cafes
            cafes = self._filter_cafes(cafe_filters)
            collection.cafes = cafes

            self.db.add(collection)
            self.db.flush()

            visibility_label = collection_data["visibility"]
            if visibility_label == "password_protected":
                visibility_label = f"password_protected (pwd: {password})"

            self.log(
                f"Created '{collection.name}' [{visibility_label}] with {len(cafes)} cafes (ID: {collection.id})",
                "success"
            )
            created_count += 1

        self.db.commit()
        self.log(f"\nTotal: {created_count} created, {skipped_count} skipped", "info")
