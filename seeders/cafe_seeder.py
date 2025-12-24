"""
Cafe seeder - Creates sample cafe data for development/testing
"""
from sqlalchemy.orm import Session
from models import Cafe, Facility
from .base_seeder import BaseSeeder


class CafeSeeder(BaseSeeder):
    """Seeder for sample cafe data"""

    @property
    def name(self) -> str:
        return "Cafes"

    # Sample cafes data
    CAFES = [
        {
            "nama": "Kopi Kenangan",
            "gambar_thumbnail": "https://example.com/kopi-kenangan.jpg",
            "no_hp": "081234567890",
            "link_website": "https://kopikenangan.com",
            "rating": 4.5,
            "range_price": "Rp 18.000 - Rp 45.000",
            "count_google_review": 1250,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Sudirman No. 123, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "qris", "take-away"]
        },
        {
            "nama": "Starbucks Reserve",
            "gambar_thumbnail": "https://example.com/starbucks.jpg",
            "no_hp": "081234567891",
            "link_website": "https://starbucks.co.id",
            "rating": 4.7,
            "range_price": "Rp 35.000 - Rp 85.000",
            "count_google_review": 3420,
            "jam_buka": "06:00 - 23:00",
            "alamat_lengkap": "Jl. Thamrin No. 1, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "toilet", "non-smoking", "qris"]
        },
        {
            "nama": "Filosofi Kopi",
            "gambar_thumbnail": "https://example.com/filosofi-kopi.jpg",
            "no_hp": "081234567892",
            "link_website": "https://filosofikopi.id",
            "rating": 4.6,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 890,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Melawai No. 45, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "outdoor", "smoking-area"]
        },
        {
            "nama": "Anomali Coffee",
            "gambar_thumbnail": "https://example.com/anomali.jpg",
            "no_hp": "081234567893",
            "link_website": "https://anomalicoffee.com",
            "rating": 4.4,
            "range_price": "Rp 30.000 - Rp 65.000",
            "count_google_review": 2100,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Kemang Raya No. 78, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "private-room", "car-parking", "reservation"]
        },
        {
            "nama": "Djournal Coffee",
            "gambar_thumbnail": "https://example.com/djournal.jpg",
            "no_hp": "081234567894",
            "link_website": "https://djournalcoffee.com",
            "rating": 4.3,
            "range_price": "Rp 28.000 - Rp 58.000",
            "count_google_review": 750,
            "jam_buka": "08:00 - 23:00",
            "alamat_lengkap": "Jl. Senopati No. 12, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "outdoor", "live-music", "smoking-area"]
        },
        {
            "nama": "Tanamera Coffee",
            "gambar_thumbnail": "https://example.com/tanamera.jpg",
            "no_hp": "081234567895",
            "link_website": "https://tanameracoffee.com",
            "rating": 4.8,
            "range_price": "Rp 35.000 - Rp 75.000",
            "count_google_review": 1680,
            "jam_buka": "07:00 - 20:00",
            "alamat_lengkap": "Jl. Panglima Polim No. 56, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "non-smoking", "qris"]
        },
        {
            "nama": "Kopi Tuku",
            "gambar_thumbnail": "https://example.com/tuku.jpg",
            "no_hp": "081234567896",
            "link_website": "https://kopituku.com",
            "rating": 4.2,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 4500,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Cipete Raya No. 23, Jakarta Selatan",
            "facility_slugs": ["wifi", "motorcycle-parking", "take-away", "qris"]
        },
        {
            "nama": "Common Grounds",
            "gambar_thumbnail": "https://example.com/common-grounds.jpg",
            "no_hp": "081234567897",
            "link_website": "https://commongrounds.co.id",
            "rating": 4.5,
            "range_price": "Rp 40.000 - Rp 90.000",
            "count_google_review": 920,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Gunawarman No. 67, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "private-room", "kids-area", "pet-friendly"]
        },
        {
            "nama": "Titik Temu Coffee",
            "gambar_thumbnail": "https://example.com/titik-temu.jpg",
            "no_hp": "081234567898",
            "link_website": "https://titiktemucoffee.com",
            "rating": 4.1,
            "range_price": "Rp 20.000 - Rp 45.000",
            "count_google_review": 560,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Radio Dalam No. 34, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "outdoor", "smoking-area", "delivery"]
        },
        {
            "nama": "Paradigma Kopi",
            "gambar_thumbnail": "https://example.com/paradigma.jpg",
            "no_hp": "081234567899",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 18.000 - Rp 40.000",
            "count_google_review": 320,
            "jam_buka": "10:00 - 21:00",
            "alamat_lengkap": "Jl. Tebet Raya No. 89, Jakarta Selatan",
            "facility_slugs": ["wifi", "power-outlet", "mushola", "motorcycle-parking", "qris"]
        }
    ]

    def run(self) -> None:
        """Create sample cafes if they don't exist"""
        # Get all facilities for mapping
        facilities = {f.slug: f for f in self.db.query(Facility).all()}

        if not facilities:
            self.log("No facilities found. Run FacilitySeeder first.", "warning")

        for cafe_data in self.CAFES:
            # Check if cafe already exists
            existing = self.db.query(Cafe).filter(
                Cafe.nama == cafe_data["nama"]
            ).first()

            if existing:
                self.log(f"Cafe '{cafe_data['nama']}' already exists (ID: {existing.id})", "skip")
                continue

            # Extract facility slugs and remove from cafe data
            facility_slugs = cafe_data.pop("facility_slugs", [])

            # Create cafe
            cafe = Cafe(**cafe_data)

            # Add facilities
            for slug in facility_slugs:
                if slug in facilities:
                    cafe.facilities.append(facilities[slug])

            self.db.add(cafe)
            self.db.flush()

            facility_count = len(cafe.facilities)
            self.log(
                f"Created cafe '{cafe_data['nama']}' with {facility_count} facilities (ID: {cafe.id})",
                "success"
            )

        self.db.commit()
