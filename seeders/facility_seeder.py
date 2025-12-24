"""
Facility seeder - Creates default cafe facilities
"""
from sqlalchemy.orm import Session
from models import Facility
from .base_seeder import BaseSeeder


class FacilitySeeder(BaseSeeder):
    """Seeder for default cafe facilities"""

    @property
    def name(self) -> str:
        return "Facilities"

    # Default facilities data
    FACILITIES = [
        {
            "name": "WiFi Gratis",
            "slug": "wifi",
            "icon": "wifi",
            "description": "Koneksi internet WiFi gratis untuk pengunjung"
        },
        {
            "name": "Mushola",
            "slug": "mushola",
            "icon": "mosque",
            "description": "Tersedia mushola untuk beribadah"
        },
        {
            "name": "Colokan Listrik",
            "slug": "power-outlet",
            "icon": "plug",
            "description": "Stop kontak tersedia di setiap meja"
        },
        {
            "name": "AC",
            "slug": "ac",
            "icon": "snowflake",
            "description": "Ruangan ber-AC dengan suhu nyaman"
        },
        {
            "name": "Private Room",
            "slug": "private-room",
            "icon": "door-closed",
            "description": "Ruangan privat untuk meeting atau acara"
        },
        {
            "name": "Outdoor Area",
            "slug": "outdoor",
            "icon": "tree",
            "description": "Area outdoor dengan pemandangan"
        },
        {
            "name": "Parkir Mobil",
            "slug": "car-parking",
            "icon": "car",
            "description": "Lahan parkir untuk mobil"
        },
        {
            "name": "Parkir Motor",
            "slug": "motorcycle-parking",
            "icon": "motorcycle",
            "description": "Lahan parkir untuk motor"
        },
        {
            "name": "Toilet",
            "slug": "toilet",
            "icon": "restroom",
            "description": "Toilet bersih tersedia"
        },
        {
            "name": "Non-Smoking Area",
            "slug": "non-smoking",
            "icon": "smoking-ban",
            "description": "Area bebas asap rokok"
        },
        {
            "name": "Smoking Area",
            "slug": "smoking-area",
            "icon": "smoking",
            "description": "Area khusus merokok tersedia"
        },
        {
            "name": "Live Music",
            "slug": "live-music",
            "icon": "music",
            "description": "Pertunjukan musik live"
        },
        {
            "name": "Pet Friendly",
            "slug": "pet-friendly",
            "icon": "paw",
            "description": "Boleh membawa hewan peliharaan"
        },
        {
            "name": "Kids Area",
            "slug": "kids-area",
            "icon": "child",
            "description": "Area bermain untuk anak-anak"
        },
        {
            "name": "Reservation",
            "slug": "reservation",
            "icon": "calendar-check",
            "description": "Menerima reservasi tempat"
        },
        {
            "name": "Delivery",
            "slug": "delivery",
            "icon": "truck",
            "description": "Layanan delivery tersedia"
        },
        {
            "name": "Take Away",
            "slug": "take-away",
            "icon": "shopping-bag",
            "description": "Pesanan bisa dibawa pulang"
        },
        {
            "name": "QRIS Payment",
            "slug": "qris",
            "icon": "qrcode",
            "description": "Pembayaran via QRIS tersedia"
        }
    ]

    def run(self) -> None:
        """Create default facilities if they don't exist"""
        for facility_data in self.FACILITIES:
            existing = self.db.query(Facility).filter(
                Facility.slug == facility_data["slug"]
            ).first()

            if existing:
                self.log(f"Facility '{facility_data['name']}' already exists (ID: {existing.id})", "skip")
            else:
                facility = Facility(**facility_data)
                self.db.add(facility)
                self.db.flush()
                self.log(f"Created facility '{facility_data['name']}' (ID: {facility.id})", "success")

        self.db.commit()
