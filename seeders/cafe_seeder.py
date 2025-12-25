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

    # Sample cafes data - 100 cafes
    CAFES = [
        # Jakarta Pusat (1-15)
        {
            "nama": "Kopi Kenangan Sudirman",
            "gambar_thumbnail": "https://example.com/kopi-kenangan.jpg",
            "no_hp": "081234567001",
            "link_website": "https://kopikenangan.com",
            "rating": 4.5,
            "range_price": "Rp 18.000 - Rp 45.000",
            "count_google_review": 1250,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Sudirman No. 123, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "qris", "take-away"]
        },
        {
            "nama": "Starbucks Reserve Thamrin",
            "gambar_thumbnail": "https://example.com/starbucks.jpg",
            "no_hp": "081234567002",
            "link_website": "https://starbucks.co.id",
            "rating": 4.7,
            "range_price": "Rp 35.000 - Rp 85.000",
            "count_google_review": 3420,
            "jam_buka": "06:00 - 23:00",
            "alamat_lengkap": "Jl. Thamrin No. 1, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "toilet", "non-smoking", "qris"]
        },
        {
            "nama": "Excelso Grand Indonesia",
            "gambar_thumbnail": "https://example.com/excelso.jpg",
            "no_hp": "081234567003",
            "link_website": "https://excelso-coffee.com",
            "rating": 4.3,
            "range_price": "Rp 30.000 - Rp 70.000",
            "count_google_review": 1890,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Grand Indonesia Mall, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "non-smoking", "qris", "reservation"]
        },
        {
            "nama": "Dua Coffee Menteng",
            "gambar_thumbnail": "https://example.com/dua-coffee.jpg",
            "no_hp": "081234567004",
            "link_website": "https://duacoffee.id",
            "rating": 4.6,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 780,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Menteng Raya No. 45, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "pet-friendly"]
        },
        {
            "nama": "Harvest Coffee Sarinah",
            "gambar_thumbnail": "https://example.com/harvest.jpg",
            "no_hp": "081234567005",
            "link_website": "https://harvestcoffee.id",
            "rating": 4.4,
            "range_price": "Rp 28.000 - Rp 60.000",
            "count_google_review": 650,
            "jam_buka": "09:00 - 21:00",
            "alamat_lengkap": "Sarinah Mall Lt. 3, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "non-smoking", "qris", "take-away"]
        },
        {
            "nama": "Bakoel Koffie Cikini",
            "gambar_thumbnail": "https://example.com/bakoel.jpg",
            "no_hp": "081234567006",
            "link_website": "https://bakoelkoffie.com",
            "rating": 4.5,
            "range_price": "Rp 20.000 - Rp 50.000",
            "count_google_review": 2340,
            "jam_buka": "07:00 - 23:00",
            "alamat_lengkap": "Jl. Cikini Raya No. 78, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "smoking-area", "outdoor", "live-music"]
        },
        {
            "nama": "Kopi Kalyan Gondangdia",
            "gambar_thumbnail": "https://example.com/kalyan.jpg",
            "no_hp": "081234567007",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 430,
            "jam_buka": "08:00 - 20:00",
            "alamat_lengkap": "Jl. Gondangdia No. 12, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "qris"]
        },
        {
            "nama": "Crematology Wahid Hasyim",
            "gambar_thumbnail": "https://example.com/crematology.jpg",
            "no_hp": "081234567008",
            "link_website": "https://crematology.id",
            "rating": 4.7,
            "range_price": "Rp 35.000 - Rp 75.000",
            "count_google_review": 1120,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Wahid Hasyim No. 56, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "non-smoking", "private-room"]
        },
        {
            "nama": "Simetri Coffee Tanah Abang",
            "gambar_thumbnail": "https://example.com/simetri.jpg",
            "no_hp": "081234567009",
            "link_website": "https://simetricoffee.com",
            "rating": 4.1,
            "range_price": "Rp 18.000 - Rp 40.000",
            "count_google_review": 290,
            "jam_buka": "08:00 - 20:00",
            "alamat_lengkap": "Jl. Tanah Abang II No. 34, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "qris", "take-away"]
        },
        {
            "nama": "Blue Lane Coffee Kebon Sirih",
            "gambar_thumbnail": "https://example.com/bluelane.jpg",
            "no_hp": "081234567010",
            "link_website": "https://bluelanecoffee.id",
            "rating": 4.3,
            "range_price": "Rp 22.000 - Rp 48.000",
            "count_google_review": 520,
            "jam_buka": "07:30 - 21:30",
            "alamat_lengkap": "Jl. Kebon Sirih No. 89, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "smoking-area"]
        },
        {
            "nama": "Giyanti Coffee Senen",
            "gambar_thumbnail": "https://example.com/giyanti.jpg",
            "no_hp": "081234567011",
            "link_website": "https://giyanticoffee.com",
            "rating": 4.6,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 890,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Senen Raya No. 23, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "mushola", "non-smoking", "reservation"]
        },
        {
            "nama": "Toko Kopi Tuku Gambir",
            "gambar_thumbnail": "https://example.com/tuku-gambir.jpg",
            "no_hp": "081234567012",
            "link_website": "https://kopituku.com",
            "rating": 4.4,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 1560,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Gambir No. 45, Jakarta Pusat",
            "facility_slugs": ["wifi", "qris", "take-away", "motorcycle-parking"]
        },
        {
            "nama": "Kapyc Coffee Kemayoran",
            "gambar_thumbnail": "https://example.com/kapyc.jpg",
            "no_hp": "081234567013",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 15.000 - Rp 38.000",
            "count_google_review": 210,
            "jam_buka": "09:00 - 20:00",
            "alamat_lengkap": "Jl. Kemayoran Gempol No. 67, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "qris"]
        },
        {
            "nama": "Sunyi House of Coffee",
            "gambar_thumbnail": "https://example.com/sunyi.jpg",
            "no_hp": "081234567014",
            "link_website": "https://sunyicoffee.id",
            "rating": 4.8,
            "range_price": "Rp 30.000 - Rp 65.000",
            "count_google_review": 2100,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Proklamasi No. 12, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "non-smoking", "private-room", "reservation"]
        },
        {
            "nama": "Ombe Kofie Menteng",
            "gambar_thumbnail": "https://example.com/ombe.jpg",
            "no_hp": "081234567015",
            "link_website": "https://ombekofie.com",
            "rating": 4.5,
            "range_price": "Rp 25.000 - Rp 58.000",
            "count_google_review": 760,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Imam Bonjol No. 34, Jakarta Pusat",
            "facility_slugs": ["wifi", "ac", "outdoor", "pet-friendly", "qris"]
        },
        # Jakarta Selatan (16-40)
        {
            "nama": "Filosofi Kopi Melawai",
            "gambar_thumbnail": "https://example.com/filosofi-kopi.jpg",
            "no_hp": "081234567016",
            "link_website": "https://filosofikopi.id",
            "rating": 4.6,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 890,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Melawai No. 45, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "outdoor", "smoking-area"]
        },
        {
            "nama": "Anomali Coffee Kemang",
            "gambar_thumbnail": "https://example.com/anomali.jpg",
            "no_hp": "081234567017",
            "link_website": "https://anomalicoffee.com",
            "rating": 4.4,
            "range_price": "Rp 30.000 - Rp 65.000",
            "count_google_review": 2100,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Kemang Raya No. 78, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "private-room", "car-parking", "reservation"]
        },
        {
            "nama": "Djournal Coffee Senopati",
            "gambar_thumbnail": "https://example.com/djournal.jpg",
            "no_hp": "081234567018",
            "link_website": "https://djournalcoffee.com",
            "rating": 4.3,
            "range_price": "Rp 28.000 - Rp 58.000",
            "count_google_review": 750,
            "jam_buka": "08:00 - 23:00",
            "alamat_lengkap": "Jl. Senopati No. 12, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "outdoor", "live-music", "smoking-area"]
        },
        {
            "nama": "Tanamera Coffee Panglima Polim",
            "gambar_thumbnail": "https://example.com/tanamera.jpg",
            "no_hp": "081234567019",
            "link_website": "https://tanameracoffee.com",
            "rating": 4.8,
            "range_price": "Rp 35.000 - Rp 75.000",
            "count_google_review": 1680,
            "jam_buka": "07:00 - 20:00",
            "alamat_lengkap": "Jl. Panglima Polim No. 56, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "non-smoking", "qris"]
        },
        {
            "nama": "Kopi Tuku Cipete",
            "gambar_thumbnail": "https://example.com/tuku.jpg",
            "no_hp": "081234567020",
            "link_website": "https://kopituku.com",
            "rating": 4.2,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 4500,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Cipete Raya No. 23, Jakarta Selatan",
            "facility_slugs": ["wifi", "motorcycle-parking", "take-away", "qris"]
        },
        {
            "nama": "Common Grounds Gunawarman",
            "gambar_thumbnail": "https://example.com/common-grounds.jpg",
            "no_hp": "081234567021",
            "link_website": "https://commongrounds.co.id",
            "rating": 4.5,
            "range_price": "Rp 40.000 - Rp 90.000",
            "count_google_review": 920,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Gunawarman No. 67, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "private-room", "kids-area", "pet-friendly"]
        },
        {
            "nama": "Titik Temu Coffee Radio Dalam",
            "gambar_thumbnail": "https://example.com/titik-temu.jpg",
            "no_hp": "081234567022",
            "link_website": "https://titiktemucoffee.com",
            "rating": 4.1,
            "range_price": "Rp 20.000 - Rp 45.000",
            "count_google_review": 560,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Radio Dalam No. 34, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "outdoor", "smoking-area", "delivery"]
        },
        {
            "nama": "Paradigma Kopi Tebet",
            "gambar_thumbnail": "https://example.com/paradigma.jpg",
            "no_hp": "081234567023",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 18.000 - Rp 40.000",
            "count_google_review": 320,
            "jam_buka": "10:00 - 21:00",
            "alamat_lengkap": "Jl. Tebet Raya No. 89, Jakarta Selatan",
            "facility_slugs": ["wifi", "power-outlet", "mushola", "motorcycle-parking", "qris"]
        },
        {
            "nama": "Kopi Nako Fatmawati",
            "gambar_thumbnail": "https://example.com/nako.jpg",
            "no_hp": "081234567024",
            "link_website": "https://kopinako.id",
            "rating": 4.3,
            "range_price": "Rp 18.000 - Rp 42.000",
            "count_google_review": 1240,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Fatmawati No. 15, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "qris", "take-away"]
        },
        {
            "nama": "Ruang Seduh Blok M",
            "gambar_thumbnail": "https://example.com/ruang-seduh.jpg",
            "no_hp": "081234567025",
            "link_website": "https://ruangseduh.com",
            "rating": 4.6,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 680,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Blok M No. 23, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "mushola", "non-smoking", "reservation"]
        },
        {
            "nama": "Upnormal Coffee Kebayoran",
            "gambar_thumbnail": "https://example.com/upnormal.jpg",
            "no_hp": "081234567026",
            "link_website": "https://upnormalcoffee.id",
            "rating": 4.2,
            "range_price": "Rp 20.000 - Rp 50.000",
            "count_google_review": 2890,
            "jam_buka": "10:00 - 24:00",
            "alamat_lengkap": "Jl. Kebayoran Baru No. 45, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "smoking-area", "delivery"]
        },
        {
            "nama": "Northsider Coffee Pondok Indah",
            "gambar_thumbnail": "https://example.com/northsider.jpg",
            "no_hp": "081234567027",
            "link_website": "https://northsidercoffee.id",
            "rating": 4.5,
            "range_price": "Rp 35.000 - Rp 70.000",
            "count_google_review": 540,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Pondok Indah No. 67, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "private-room", "car-parking", "kids-area"]
        },
        {
            "nama": "Komunal 88 Dharmawangsa",
            "gambar_thumbnail": "https://example.com/komunal.jpg",
            "no_hp": "081234567028",
            "link_website": "https://komunal88.com",
            "rating": 4.4,
            "range_price": "Rp 28.000 - Rp 62.000",
            "count_google_review": 420,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Dharmawangsa No. 88, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "pet-friendly"]
        },
        {
            "nama": "Soko Coffee Ampera",
            "gambar_thumbnail": "https://example.com/soko.jpg",
            "no_hp": "081234567029",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 18.000 - Rp 45.000",
            "count_google_review": 380,
            "jam_buka": "07:30 - 21:00",
            "alamat_lengkap": "Jl. Ampera Raya No. 34, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "mushola", "qris", "motorcycle-parking"]
        },
        {
            "nama": "Kopi Janji Jiwa Cilandak",
            "gambar_thumbnail": "https://example.com/janji-jiwa.jpg",
            "no_hp": "081234567030",
            "link_website": "https://janjijiwa.id",
            "rating": 4.3,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 3200,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Cilandak KKO No. 12, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "qris", "take-away", "delivery"]
        },
        {
            "nama": "Two Cents Coffee Pejaten",
            "gambar_thumbnail": "https://example.com/two-cents.jpg",
            "no_hp": "081234567031",
            "link_website": "https://twocentscoffee.id",
            "rating": 4.5,
            "range_price": "Rp 28.000 - Rp 58.000",
            "count_google_review": 620,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Pejaten Raya No. 56, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "non-smoking"]
        },
        {
            "nama": "Kopi Se-Indonesia Mampang",
            "gambar_thumbnail": "https://example.com/kopi-se-indonesia.jpg",
            "no_hp": "081234567032",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 20.000 - Rp 48.000",
            "count_google_review": 450,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Mampang Prapatan No. 78, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "mushola", "smoking-area", "qris"]
        },
        {
            "nama": "Maxx Coffee Gandaria",
            "gambar_thumbnail": "https://example.com/maxx.jpg",
            "no_hp": "081234567033",
            "link_website": "https://maxxcoffee.com",
            "rating": 4.0,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 890,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Gandaria City Mall, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "non-smoking", "qris", "reservation"]
        },
        {
            "nama": "Kayu Manis Coffee Lebak Bulus",
            "gambar_thumbnail": "https://example.com/kayu-manis.jpg",
            "no_hp": "081234567034",
            "link_website": "https://kayumaniscoffee.id",
            "rating": 4.4,
            "range_price": "Rp 22.000 - Rp 50.000",
            "count_google_review": 340,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Lebak Bulus Raya No. 23, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "pet-friendly"]
        },
        {
            "nama": "Kopi Kulo Pasar Minggu",
            "gambar_thumbnail": "https://example.com/kulo.jpg",
            "no_hp": "081234567035",
            "link_website": "https://kopikulo.id",
            "rating": 4.1,
            "range_price": "Rp 15.000 - Rp 38.000",
            "count_google_review": 1560,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Pasar Minggu Raya No. 45, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "qris", "take-away", "motorcycle-parking"]
        },
        {
            "nama": "Kopi Lain Hati Kalibata",
            "gambar_thumbnail": "https://example.com/lain-hati.jpg",
            "no_hp": "081234567036",
            "link_website": "https://kopilainhati.id",
            "rating": 4.3,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 2100,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Kalibata Raya No. 67, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "qris", "delivery"]
        },
        {
            "nama": "Fore Coffee Kemang",
            "gambar_thumbnail": "https://example.com/fore.jpg",
            "no_hp": "081234567037",
            "link_website": "https://fore.coffee",
            "rating": 4.5,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 1890,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Kemang Timur No. 89, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "non-smoking", "qris"]
        },
        {
            "nama": "Ragusa Italian Coffee Senayan",
            "gambar_thumbnail": "https://example.com/ragusa.jpg",
            "no_hp": "081234567038",
            "link_website": "https://ragusa.co.id",
            "rating": 4.6,
            "range_price": "Rp 35.000 - Rp 80.000",
            "count_google_review": 1450,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Senayan City Mall, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "non-smoking", "reservation", "qris"]
        },
        {
            "nama": "Kopi Konnichiwa Tebet",
            "gambar_thumbnail": "https://example.com/konnichiwa.jpg",
            "no_hp": "081234567039",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 20.000 - Rp 45.000",
            "count_google_review": 560,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Tebet Utara No. 12, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "outdoor", "smoking-area", "live-music"]
        },
        {
            "nama": "Sejiwa Coffee Blok A",
            "gambar_thumbnail": "https://example.com/sejiwa.jpg",
            "no_hp": "081234567040",
            "link_website": "https://sejiwacoffee.id",
            "rating": 4.4,
            "range_price": "Rp 22.000 - Rp 52.000",
            "count_google_review": 430,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Pasar Blok A, Jakarta Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "take-away"]
        },
        # Jakarta Barat (41-55)
        {
            "nama": "Jakarta Coffee House Taman Anggrek",
            "gambar_thumbnail": "https://example.com/jch.jpg",
            "no_hp": "081234567041",
            "link_website": "https://jakartacoffeehouse.id",
            "rating": 4.5,
            "range_price": "Rp 30.000 - Rp 65.000",
            "count_google_review": 780,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Mall Taman Anggrek, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "non-smoking", "reservation", "qris"]
        },
        {
            "nama": "Kopi Oey Grogol",
            "gambar_thumbnail": "https://example.com/kopi-oey.jpg",
            "no_hp": "081234567042",
            "link_website": "https://kopioey.com",
            "rating": 4.3,
            "range_price": "Rp 20.000 - Rp 48.000",
            "count_google_review": 1230,
            "jam_buka": "08:00 - 23:00",
            "alamat_lengkap": "Jl. Grogol Petamburan No. 45, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "smoking-area", "live-music", "outdoor"]
        },
        {
            "nama": "Nongkrong Coffee Kebon Jeruk",
            "gambar_thumbnail": "https://example.com/nongkrong.jpg",
            "no_hp": "081234567043",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 18.000 - Rp 42.000",
            "count_google_review": 450,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Kebon Jeruk Raya No. 78, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "qris", "motorcycle-parking"]
        },
        {
            "nama": "Kopi Masa Kini Slipi",
            "gambar_thumbnail": "https://example.com/masa-kini.jpg",
            "no_hp": "081234567044",
            "link_website": "https://kopimasakini.id",
            "rating": 4.2,
            "range_price": "Rp 15.000 - Rp 38.000",
            "count_google_review": 670,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Slipi Raya No. 12, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "mushola", "take-away", "delivery"]
        },
        {
            "nama": "Point Coffee Central Park",
            "gambar_thumbnail": "https://example.com/point-coffee.jpg",
            "no_hp": "081234567045",
            "link_website": "https://pointcoffee.id",
            "rating": 4.4,
            "range_price": "Rp 22.000 - Rp 50.000",
            "count_google_review": 1890,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Central Park Mall, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "non-smoking", "qris", "reservation"]
        },
        {
            "nama": "Kopi Chuseyo Puri",
            "gambar_thumbnail": "https://example.com/chuseyo.jpg",
            "no_hp": "081234567046",
            "link_website": "https://kopichuseyo.com",
            "rating": 4.0,
            "range_price": "Rp 18.000 - Rp 40.000",
            "count_google_review": 340,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Puri Indah No. 23, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "kids-area"]
        },
        {
            "nama": "Dailydose Coffee Tomang",
            "gambar_thumbnail": "https://example.com/dailydose.jpg",
            "no_hp": "081234567047",
            "link_website": "https://dailydosecoffee.id",
            "rating": 4.3,
            "range_price": "Rp 20.000 - Rp 48.000",
            "count_google_review": 520,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Tomang Raya No. 56, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "smoking-area", "qris", "take-away"]
        },
        {
            "nama": "Kedai Kopi Tenong Cengkareng",
            "gambar_thumbnail": "https://example.com/tenong.jpg",
            "no_hp": "081234567048",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 280,
            "jam_buka": "08:00 - 20:00",
            "alamat_lengkap": "Jl. Cengkareng Raya No. 89, Jakarta Barat",
            "facility_slugs": ["wifi", "mushola", "motorcycle-parking", "qris"]
        },
        {
            "nama": "Groove Coffee Pluit",
            "gambar_thumbnail": "https://example.com/groove.jpg",
            "no_hp": "081234567049",
            "link_website": "https://groovecoffee.id",
            "rating": 4.5,
            "range_price": "Rp 28.000 - Rp 60.000",
            "count_google_review": 650,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Pluit Selatan No. 34, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "pet-friendly"]
        },
        {
            "nama": "Kopi Manyar Jelambar",
            "gambar_thumbnail": "https://example.com/manyar.jpg",
            "no_hp": "081234567050",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 15.000 - Rp 38.000",
            "count_google_review": 210,
            "jam_buka": "07:30 - 21:00",
            "alamat_lengkap": "Jl. Jelambar Baru No. 67, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "take-away", "delivery"]
        },
        {
            "nama": "Baked Coffee Meruya",
            "gambar_thumbnail": "https://example.com/baked.jpg",
            "no_hp": "081234567051",
            "link_website": "https://bakedcoffee.id",
            "rating": 4.4,
            "range_price": "Rp 25.000 - Rp 55.000",
            "count_google_review": 430,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Meruya Ilir No. 12, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "non-smoking", "kids-area", "reservation"]
        },
        {
            "nama": "Kopi Nyantai Joglo",
            "gambar_thumbnail": "https://example.com/nyantai.jpg",
            "no_hp": "081234567052",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 18.000 - Rp 42.000",
            "count_google_review": 380,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Joglo Raya No. 45, Jakarta Barat",
            "facility_slugs": ["wifi", "outdoor", "smoking-area", "live-music", "qris"]
        },
        {
            "nama": "Asymmetric Coffee Kedoya",
            "gambar_thumbnail": "https://example.com/asymmetric.jpg",
            "no_hp": "081234567053",
            "link_website": "https://asymmetriccoffee.id",
            "rating": 4.6,
            "range_price": "Rp 30.000 - Rp 65.000",
            "count_google_review": 560,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Kedoya Raya No. 78, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "power-outlet", "private-room", "reservation"]
        },
        {
            "nama": "Woodpecker Coffee Tanjung Duren",
            "gambar_thumbnail": "https://example.com/woodpecker.jpg",
            "no_hp": "081234567054",
            "link_website": "https://woodpeckercoffee.com",
            "rating": 4.3,
            "range_price": "Rp 22.000 - Rp 52.000",
            "count_google_review": 670,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Tanjung Duren Raya No. 23, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "outdoor", "pet-friendly", "qris"]
        },
        {
            "nama": "Weekend Coffee Kalideres",
            "gambar_thumbnail": "https://example.com/weekend.jpg",
            "no_hp": "081234567055",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 18.000 - Rp 40.000",
            "count_google_review": 290,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Kalideres Raya No. 56, Jakarta Barat",
            "facility_slugs": ["wifi", "ac", "mushola", "car-parking", "take-away"]
        },
        # Jakarta Timur (56-70)
        {
            "nama": "Kopi Kalina Cawang",
            "gambar_thumbnail": "https://example.com/kalina.jpg",
            "no_hp": "081234567056",
            "link_website": "https://kopikalina.id",
            "rating": 4.4,
            "range_price": "Rp 20.000 - Rp 48.000",
            "count_google_review": 560,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Cawang Baru No. 12, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "qris"]
        },
        {
            "nama": "Starbucks Rawamangun",
            "gambar_thumbnail": "https://example.com/starbucks-rwm.jpg",
            "no_hp": "081234567057",
            "link_website": "https://starbucks.co.id",
            "rating": 4.5,
            "range_price": "Rp 35.000 - Rp 85.000",
            "count_google_review": 1890,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Rawamangun Raya No. 45, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "non-smoking", "toilet", "qris"]
        },
        {
            "nama": "Warung Kopi Pejuang Jatinegara",
            "gambar_thumbnail": "https://example.com/pejuang.jpg",
            "no_hp": "081234567058",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 12.000 - Rp 30.000",
            "count_google_review": 780,
            "jam_buka": "06:00 - 23:00",
            "alamat_lengkap": "Jl. Jatinegara Barat No. 78, Jakarta Timur",
            "facility_slugs": ["wifi", "smoking-area", "outdoor", "motorcycle-parking"]
        },
        {
            "nama": "Kopi Klotok Pulomas",
            "gambar_thumbnail": "https://example.com/klotok.jpg",
            "no_hp": "081234567059",
            "link_website": "https://kopiklotok.com",
            "rating": 4.3,
            "range_price": "Rp 22.000 - Rp 50.000",
            "count_google_review": 430,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Pulomas Raya No. 23, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "outdoor", "live-music", "qris"]
        },
        {
            "nama": "Toby's Estate Kelapa Gading",
            "gambar_thumbnail": "https://example.com/tobys.jpg",
            "no_hp": "081234567060",
            "link_website": "https://tobysestate.co.id",
            "rating": 4.7,
            "range_price": "Rp 40.000 - Rp 85.000",
            "count_google_review": 1240,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Mall Kelapa Gading, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "non-smoking", "private-room", "reservation"]
        },
        {
            "nama": "Kopi Kenangan Buaran",
            "gambar_thumbnail": "https://example.com/kenangan-buaran.jpg",
            "no_hp": "081234567061",
            "link_website": "https://kopikenangan.com",
            "rating": 4.3,
            "range_price": "Rp 18.000 - Rp 45.000",
            "count_google_review": 890,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Buaran Raya No. 56, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "qris", "take-away", "delivery"]
        },
        {
            "nama": "Lawas Coffee Pondok Kelapa",
            "gambar_thumbnail": "https://example.com/lawas.jpg",
            "no_hp": "081234567062",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 15.000 - Rp 38.000",
            "count_google_review": 320,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Pondok Kelapa No. 89, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "power-outlet", "smoking-area", "motorcycle-parking"]
        },
        {
            "nama": "Kopi Dari Hati Cipinang",
            "gambar_thumbnail": "https://example.com/dari-hati.jpg",
            "no_hp": "081234567063",
            "link_website": "https://kopidarihati.id",
            "rating": 4.4,
            "range_price": "Rp 18.000 - Rp 42.000",
            "count_google_review": 560,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Cipinang Besar No. 12, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "mushola", "qris", "take-away"]
        },
        {
            "nama": "Urban Coffee Duren Sawit",
            "gambar_thumbnail": "https://example.com/urban.jpg",
            "no_hp": "081234567064",
            "link_website": "https://urbancoffee.id",
            "rating": 4.2,
            "range_price": "Rp 20.000 - Rp 50.000",
            "count_google_review": 450,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Duren Sawit Raya No. 34, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "outdoor", "kids-area", "car-parking"]
        },
        {
            "nama": "Kopi Sedulur Kramat Jati",
            "gambar_thumbnail": "https://example.com/sedulur.jpg",
            "no_hp": "081234567065",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 12.000 - Rp 30.000",
            "count_google_review": 210,
            "jam_buka": "06:00 - 22:00",
            "alamat_lengkap": "Jl. Kramat Jati No. 67, Jakarta Timur",
            "facility_slugs": ["wifi", "outdoor", "smoking-area", "motorcycle-parking"]
        },
        {
            "nama": "Blueprint Coffee Sunter",
            "gambar_thumbnail": "https://example.com/blueprint.jpg",
            "no_hp": "081234567066",
            "link_website": "https://blueprintcoffee.id",
            "rating": 4.5,
            "range_price": "Rp 28.000 - Rp 60.000",
            "count_google_review": 680,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Sunter Agung No. 78, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "power-outlet", "non-smoking", "reservation"]
        },
        {
            "nama": "Kedai Kopi Makmur Pulogadung",
            "gambar_thumbnail": "https://example.com/makmur.jpg",
            "no_hp": "081234567067",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 380,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Pulogadung No. 23, Jakarta Timur",
            "facility_slugs": ["wifi", "mushola", "smoking-area", "qris"]
        },
        {
            "nama": "Coffee Lab Cibubur",
            "gambar_thumbnail": "https://example.com/coffee-lab.jpg",
            "no_hp": "081234567068",
            "link_website": "https://coffeelab.id",
            "rating": 4.6,
            "range_price": "Rp 30.000 - Rp 65.000",
            "count_google_review": 920,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Cibubur Raya No. 45, Jakarta Timur",
            "facility_slugs": ["wifi", "ac", "private-room", "kids-area", "car-parking"]
        },
        {
            "nama": "Nongki Coffee Lubang Buaya",
            "gambar_thumbnail": "https://example.com/nongki.jpg",
            "no_hp": "081234567069",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 15.000 - Rp 38.000",
            "count_google_review": 240,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Lubang Buaya No. 56, Jakarta Timur",
            "facility_slugs": ["wifi", "outdoor", "smoking-area", "live-music"]
        },
        {
            "nama": "Sederhana Coffee Pasar Rebo",
            "gambar_thumbnail": "https://example.com/sederhana.jpg",
            "no_hp": "081234567070",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 12.000 - Rp 32.000",
            "count_google_review": 320,
            "jam_buka": "06:00 - 22:00",
            "alamat_lengkap": "Jl. Pasar Rebo No. 89, Jakarta Timur",
            "facility_slugs": ["wifi", "mushola", "motorcycle-parking", "take-away"]
        },
        # Jakarta Utara (71-85)
        {
            "nama": "Coffee Times Pluit Village",
            "gambar_thumbnail": "https://example.com/coffee-times.jpg",
            "no_hp": "081234567071",
            "link_website": "https://coffeetimes.id",
            "rating": 4.4,
            "range_price": "Rp 28.000 - Rp 60.000",
            "count_google_review": 780,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Pluit Village Mall, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "non-smoking", "kids-area", "qris"]
        },
        {
            "nama": "Kopi Angkringan PIK",
            "gambar_thumbnail": "https://example.com/angkringan.jpg",
            "no_hp": "081234567072",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 15.000 - Rp 40.000",
            "count_google_review": 890,
            "jam_buka": "16:00 - 02:00",
            "alamat_lengkap": "Pantai Indah Kapuk No. 12, Jakarta Utara",
            "facility_slugs": ["wifi", "outdoor", "smoking-area", "live-music", "motorcycle-parking"]
        },
        {
            "nama": "Bungkus Coffee Koja",
            "gambar_thumbnail": "https://example.com/bungkus.jpg",
            "no_hp": "081234567073",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 12.000 - Rp 30.000",
            "count_google_review": 340,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Koja Raya No. 45, Jakarta Utara",
            "facility_slugs": ["wifi", "smoking-area", "take-away", "delivery"]
        },
        {
            "nama": "Klasik Coffee Kelapa Gading",
            "gambar_thumbnail": "https://example.com/klasik.jpg",
            "no_hp": "081234567074",
            "link_website": "https://klasikcoffee.id",
            "rating": 4.5,
            "range_price": "Rp 25.000 - Rp 58.000",
            "count_google_review": 1120,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Boulevard Kelapa Gading No. 78, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "power-outlet", "outdoor", "pet-friendly"]
        },
        {
            "nama": "Minum Kopi Ancol",
            "gambar_thumbnail": "https://example.com/minum-kopi.jpg",
            "no_hp": "081234567075",
            "link_website": "https://minumkopi.id",
            "rating": 4.3,
            "range_price": "Rp 20.000 - Rp 50.000",
            "count_google_review": 670,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Jl. Ancol Barat No. 23, Jakarta Utara",
            "facility_slugs": ["wifi", "outdoor", "smoking-area", "car-parking", "qris"]
        },
        {
            "nama": "Kopi Susu Tetangga Tanjung Priok",
            "gambar_thumbnail": "https://example.com/tetangga.jpg",
            "no_hp": "081234567076",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 15.000 - Rp 35.000",
            "count_google_review": 450,
            "jam_buka": "07:00 - 21:00",
            "alamat_lengkap": "Jl. Tanjung Priok No. 56, Jakarta Utara",
            "facility_slugs": ["wifi", "mushola", "take-away", "motorcycle-parking"]
        },
        {
            "nama": "Senja Coffee Pademangan",
            "gambar_thumbnail": "https://example.com/senja.jpg",
            "no_hp": "081234567077",
            "link_website": "https://senjacoffee.id",
            "rating": 4.4,
            "range_price": "Rp 22.000 - Rp 52.000",
            "count_google_review": 560,
            "jam_buka": "15:00 - 23:00",
            "alamat_lengkap": "Jl. Pademangan Raya No. 89, Jakarta Utara",
            "facility_slugs": ["wifi", "outdoor", "live-music", "smoking-area", "qris"]
        },
        {
            "nama": "Morning Glory Coffee Sunter",
            "gambar_thumbnail": "https://example.com/morning-glory.jpg",
            "no_hp": "081234567078",
            "link_website": "https://morningglory.id",
            "rating": 4.6,
            "range_price": "Rp 28.000 - Rp 62.000",
            "count_google_review": 890,
            "jam_buka": "06:00 - 18:00",
            "alamat_lengkap": "Jl. Sunter Permai No. 12, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "power-outlet", "non-smoking", "reservation"]
        },
        {
            "nama": "Roastery Coffee Penjaringan",
            "gambar_thumbnail": "https://example.com/roastery.jpg",
            "no_hp": "081234567079",
            "link_website": "https://roasterycoffee.id",
            "rating": 4.5,
            "range_price": "Rp 30.000 - Rp 70.000",
            "count_google_review": 720,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Penjaringan Raya No. 34, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "private-room", "non-smoking", "qris"]
        },
        {
            "nama": "Kopi Sejuta Rasa Muara Karang",
            "gambar_thumbnail": "https://example.com/sejuta-rasa.jpg",
            "no_hp": "081234567080",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 18.000 - Rp 45.000",
            "count_google_review": 430,
            "jam_buka": "09:00 - 22:00",
            "alamat_lengkap": "Jl. Muara Karang No. 67, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "outdoor", "smoking-area", "delivery"]
        },
        {
            "nama": "Brew & Beans Pantai Indah Kapuk",
            "gambar_thumbnail": "https://example.com/brew-beans.jpg",
            "no_hp": "081234567081",
            "link_website": "https://brewbeans.id",
            "rating": 4.7,
            "range_price": "Rp 35.000 - Rp 80.000",
            "count_google_review": 1340,
            "jam_buka": "08:00 - 23:00",
            "alamat_lengkap": "PIK Avenue, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "power-outlet", "private-room", "pet-friendly"]
        },
        {
            "nama": "Kopi Ndeso Cilincing",
            "gambar_thumbnail": "https://example.com/ndeso.jpg",
            "no_hp": "081234567082",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 10.000 - Rp 28.000",
            "count_google_review": 210,
            "jam_buka": "06:00 - 21:00",
            "alamat_lengkap": "Jl. Cilincing Raya No. 78, Jakarta Utara",
            "facility_slugs": ["outdoor", "smoking-area", "motorcycle-parking"]
        },
        {
            "nama": "Caffeine Lab MOI",
            "gambar_thumbnail": "https://example.com/caffeine-lab.jpg",
            "no_hp": "081234567083",
            "link_website": "https://caffeinelab.id",
            "rating": 4.4,
            "range_price": "Rp 28.000 - Rp 65.000",
            "count_google_review": 780,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Mall of Indonesia, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "non-smoking", "kids-area", "qris"]
        },
        {
            "nama": "Kopi Pelangi Pluit",
            "gambar_thumbnail": "https://example.com/pelangi.jpg",
            "no_hp": "081234567084",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 18.000 - Rp 42.000",
            "count_google_review": 340,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Pluit Sakti No. 23, Jakarta Utara",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "take-away"]
        },
        {
            "nama": "Sunrise Coffee Marunda",
            "gambar_thumbnail": "https://example.com/sunrise.jpg",
            "no_hp": "081234567085",
            "link_website": "https://sunrisecoffee.id",
            "rating": 4.3,
            "range_price": "Rp 20.000 - Rp 48.000",
            "count_google_review": 450,
            "jam_buka": "05:00 - 20:00",
            "alamat_lengkap": "Jl. Marunda Raya No. 45, Jakarta Utara",
            "facility_slugs": ["wifi", "outdoor", "car-parking", "qris"]
        },
        # Depok, Tangerang, Bekasi (86-100)
        {
            "nama": "Kopi Margonda Depok",
            "gambar_thumbnail": "https://example.com/margonda.jpg",
            "no_hp": "081234567086",
            "link_website": "https://kopimargonda.id",
            "rating": 4.3,
            "range_price": "Rp 15.000 - Rp 40.000",
            "count_google_review": 1230,
            "jam_buka": "07:00 - 23:00",
            "alamat_lengkap": "Jl. Margonda Raya No. 56, Depok",
            "facility_slugs": ["wifi", "ac", "power-outlet", "mushola", "motorcycle-parking"]
        },
        {
            "nama": "Campus Coffee UI",
            "gambar_thumbnail": "https://example.com/campus.jpg",
            "no_hp": "081234567087",
            "link_website": None,
            "rating": 4.4,
            "range_price": "Rp 12.000 - Rp 35.000",
            "count_google_review": 890,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Kampus UI Depok",
            "facility_slugs": ["wifi", "power-outlet", "outdoor", "take-away"]
        },
        {
            "nama": "Kopi Nusantara BSD",
            "gambar_thumbnail": "https://example.com/nusantara.jpg",
            "no_hp": "081234567088",
            "link_website": "https://kopinusantara.id",
            "rating": 4.5,
            "range_price": "Rp 25.000 - Rp 58.000",
            "count_google_review": 780,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "BSD City Walk, Tangerang Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "kids-area", "qris"]
        },
        {
            "nama": "Morning Brew Alam Sutera",
            "gambar_thumbnail": "https://example.com/morning-brew.jpg",
            "no_hp": "081234567089",
            "link_website": "https://morningbrew.id",
            "rating": 4.6,
            "range_price": "Rp 30.000 - Rp 68.000",
            "count_google_review": 1120,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Mall @ Alam Sutera, Tangerang",
            "facility_slugs": ["wifi", "ac", "non-smoking", "private-room", "reservation"]
        },
        {
            "nama": "Kopi Gading Serpong",
            "gambar_thumbnail": "https://example.com/gading-serpong.jpg",
            "no_hp": "081234567090",
            "link_website": "https://kopigadingserpong.id",
            "rating": 4.3,
            "range_price": "Rp 20.000 - Rp 50.000",
            "count_google_review": 670,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Summarecon Serpong, Tangerang",
            "facility_slugs": ["wifi", "ac", "outdoor", "pet-friendly", "car-parking"]
        },
        {
            "nama": "Santai Coffee Karawaci",
            "gambar_thumbnail": "https://example.com/santai.jpg",
            "no_hp": "081234567091",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 15.000 - Rp 38.000",
            "count_google_review": 430,
            "jam_buka": "09:00 - 21:00",
            "alamat_lengkap": "Lippo Karawaci, Tangerang",
            "facility_slugs": ["wifi", "ac", "smoking-area", "qris", "take-away"]
        },
        {
            "nama": "Kopi Bekasi Square",
            "gambar_thumbnail": "https://example.com/bekasi-square.jpg",
            "no_hp": "081234567092",
            "link_website": "https://kopibekasisquare.id",
            "rating": 4.4,
            "range_price": "Rp 22.000 - Rp 52.000",
            "count_google_review": 890,
            "jam_buka": "10:00 - 22:00",
            "alamat_lengkap": "Bekasi Square Mall, Bekasi",
            "facility_slugs": ["wifi", "ac", "power-outlet", "non-smoking", "kids-area"]
        },
        {
            "nama": "Java Coffee Harapan Indah",
            "gambar_thumbnail": "https://example.com/java.jpg",
            "no_hp": "081234567093",
            "link_website": "https://javacoffee.id",
            "rating": 4.2,
            "range_price": "Rp 18.000 - Rp 45.000",
            "count_google_review": 560,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Harapan Indah Boulevard, Bekasi",
            "facility_slugs": ["wifi", "ac", "mushola", "car-parking", "qris"]
        },
        {
            "nama": "Kopi Summarecon Bekasi",
            "gambar_thumbnail": "https://example.com/summarecon-bekasi.jpg",
            "no_hp": "081234567094",
            "link_website": None,
            "rating": 4.3,
            "range_price": "Rp 20.000 - Rp 50.000",
            "count_google_review": 780,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Summarecon Bekasi, Bekasi",
            "facility_slugs": ["wifi", "ac", "outdoor", "pet-friendly", "delivery"]
        },
        {
            "nama": "Warung Kopi Cikarang",
            "gambar_thumbnail": "https://example.com/cikarang.jpg",
            "no_hp": "081234567095",
            "link_website": None,
            "rating": 4.0,
            "range_price": "Rp 12.000 - Rp 32.000",
            "count_google_review": 340,
            "jam_buka": "06:00 - 22:00",
            "alamat_lengkap": "Jl. Cikarang Raya No. 23, Bekasi",
            "facility_slugs": ["wifi", "smoking-area", "outdoor", "motorcycle-parking"]
        },
        {
            "nama": "Kopi Bintaro Exchange",
            "gambar_thumbnail": "https://example.com/bintaro.jpg",
            "no_hp": "081234567096",
            "link_website": "https://kopibintaro.id",
            "rating": 4.5,
            "range_price": "Rp 28.000 - Rp 62.000",
            "count_google_review": 920,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Bintaro Xchange Mall, Tangerang Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "private-room", "reservation"]
        },
        {
            "nama": "Artisan Coffee Cinere",
            "gambar_thumbnail": "https://example.com/artisan.jpg",
            "no_hp": "081234567097",
            "link_website": "https://artisancoffee.id",
            "rating": 4.6,
            "range_price": "Rp 30.000 - Rp 70.000",
            "count_google_review": 670,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Cinere Bellevue Mall, Depok",
            "facility_slugs": ["wifi", "ac", "non-smoking", "kids-area", "qris"]
        },
        {
            "nama": "Kopi Metro Bekasi",
            "gambar_thumbnail": "https://example.com/metro.jpg",
            "no_hp": "081234567098",
            "link_website": None,
            "rating": 4.2,
            "range_price": "Rp 18.000 - Rp 45.000",
            "count_google_review": 450,
            "jam_buka": "07:00 - 22:00",
            "alamat_lengkap": "Jl. Ahmad Yani No. 45, Bekasi",
            "facility_slugs": ["wifi", "ac", "mushola", "take-away", "delivery"]
        },
        {
            "nama": "Green Valley Coffee Sawangan",
            "gambar_thumbnail": "https://example.com/green-valley.jpg",
            "no_hp": "081234567099",
            "link_website": "https://greenvalleycoffee.id",
            "rating": 4.4,
            "range_price": "Rp 22.000 - Rp 55.000",
            "count_google_review": 380,
            "jam_buka": "08:00 - 21:00",
            "alamat_lengkap": "Jl. Sawangan Raya No. 67, Depok",
            "facility_slugs": ["wifi", "outdoor", "pet-friendly", "live-music", "car-parking"]
        },
        {
            "nama": "Kopi Pamulang Square",
            "gambar_thumbnail": "https://example.com/pamulang.jpg",
            "no_hp": "081234567100",
            "link_website": None,
            "rating": 4.1,
            "range_price": "Rp 15.000 - Rp 40.000",
            "count_google_review": 290,
            "jam_buka": "08:00 - 22:00",
            "alamat_lengkap": "Pamulang Square, Tangerang Selatan",
            "facility_slugs": ["wifi", "ac", "power-outlet", "smoking-area", "qris"]
        }
    ]

    def run(self) -> None:
        """Create sample cafes if they don't exist"""
        # Get all facilities for mapping
        facilities = {f.slug: f for f in self.db.query(Facility).all()}

        if not facilities:
            self.log("No facilities found. Run FacilitySeeder first.", "warning")

        created_count = 0
        skipped_count = 0

        for cafe_data in self.CAFES:
            # Check if cafe already exists
            existing = self.db.query(Cafe).filter(
                Cafe.nama == cafe_data["nama"]
            ).first()

            if existing:
                self.log(f"Cafe '{cafe_data['nama']}' already exists (ID: {existing.id})", "skip")
                skipped_count += 1
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
                f"Created cafe '{cafe.nama}' with {facility_count} facilities (ID: {cafe.id})",
                "success"
            )
            created_count += 1

        self.db.commit()
        self.log(f"\nTotal: {created_count} created, {skipped_count} skipped", "info")
