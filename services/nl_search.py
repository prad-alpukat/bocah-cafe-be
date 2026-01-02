from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from config import settings
from sqlalchemy.orm import Session
from sqlalchemy import or_, case
from models import Cafe, Facility, Collection
import json
import re


class ParsedQuery(BaseModel):
    """Structured query parsed from natural language"""
    is_relevant: bool = True  # False jika query tidak relevan dengan cafe
    query_type: str = "search"  # "search", "identity", "greeting", "irrelevant"
    search_text: Optional[str] = None
    facilities: List[str] = []
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    price_category: Optional[str] = None  # "murah", "sedang", "mahal"
    location: Optional[str] = None
    intent: Optional[str] = None  # "kerja", "nongkrong", "meeting", "foto", etc.
    sort_by: Optional[str] = None  # "rating", "reviews", "terbaru"
    entity_type: str = "cafe"  # "cafe", "facility", "collection", "all"
    limit: Optional[int] = None  # jumlah hasil yang diminta user (e.g. "3 cafe" -> 3)


class NLSearchService:
    """Natural Language Search Service using Groq (primary) or Gemini (fallback)"""

    SYSTEM_PROMPT = """Kamu adalah parser query pencarian untuk aplikasi direktori kafe.
Tugas kamu adalah mengekstrak informasi terstruktur dari query natural language user.

Fasilitas yang tersedia (gunakan slug):
- wifi: WiFi gratis
- ac: AC / pendingin ruangan
- mushola: Mushola / tempat ibadah
- toilet: Toilet
- parking: Parkir
- outdoor: Area outdoor
- indoor: Area indoor
- smoking-area: Smoking area
- meeting-room: Ruang meeting
- power-outlet: Stop kontak / colokan
- pet-friendly: Pet friendly
- live-music: Live music
- board-games: Board games

Kategori harga:
- "murah": range_price mengandung < 30.000
- "sedang": range_price mengandung 30.000 - 70.000
- "mahal": range_price mengandung > 70.000

Intent/tujuan umum:
- "kerja": user ingin bekerja/WFH (biasanya butuh wifi, power outlet)
- "nongkrong": user ingin hangout santai
- "meeting": user ingin meeting (biasanya butuh meeting room, wifi)
- "foto": user ingin tempat aesthetic untuk foto
- "belajar": user ingin belajar (mirip kerja)
- "kencan": user ingin date/romantic

Entity types:
- "cafe": mencari kafe
- "facility": mencari fasilitas
- "collection": mencari koleksi/kurasi
- "all": mencari semua

PENTING tentang query_type:
- "search": query mencari cafe/collection/facility (default)
- "identity": user bertanya tentang siapa kamu/bot ini (contoh: "kamu siapa?", "siapa kamu", "lu siapa", "what are you")
- "creator": user bertanya siapa yang membuat app/bot ini (contoh: "siapa yang buat", "who made this", "siapa pembuat", "developer nya siapa")
- "greeting": user menyapa (contoh: "halo", "hi", "selamat pagi")
- "irrelevant": query tidak relevan dengan cafe sama sekali (contoh: "siapa presiden", "apa itu python", "cuaca hari ini")

Jika query_type bukan "search", set is_relevant = false.

PENTING tentang search_text:
- search_text HANYA diisi jika user mencari nama cafe SPESIFIK atau kata kunci unik
- JANGAN isi search_text dengan kata-kata umum seperti: nongkrong, nongki, kerja, santai, ngopi, kopi, cafe, coffee
- Jika user bilang "cafe untuk nongki" atau "tempat nongkrong", itu adalah INTENT bukan search_text
- search_text = null untuk kebanyakan query, kecuali user sebut nama spesifik

PENTING tentang limit:
- Jika user menyebutkan ANGKA di awal query seperti "3 cafe", "5 tempat nongkrong", "10 kafe wifi", extract angka tersebut sebagai limit
- Jika user bilang "beberapa" atau "few" set limit = 3
- Jika tidak ada angka spesifik, set limit = null (akan pakai default)
- Limit maksimal 100

Respond dalam format JSON SAJA tanpa markdown code block:
{
    "is_relevant": true atau false,
    "query_type": "search" atau "identity" atau "creator" atau "greeting" atau "irrelevant",
    "search_text": "HANYA nama cafe spesifik atau null",
    "facilities": ["slug-facility-1", "slug-facility-2"],
    "min_rating": null atau angka 0-5,
    "max_rating": null atau angka 0-5,
    "price_category": null atau "murah"/"sedang"/"mahal",
    "location": "nama lokasi/kota atau null",
    "intent": null atau intent yang terdeteksi,
    "sort_by": null atau "rating"/"reviews"/"terbaru",
    "entity_type": "cafe" atau "facility" atau "collection" atau "all",
    "limit": null atau angka 1-100
}

Contoh:
Query: "kafe dengan wifi di bandung yang murah buat kerja"
{
    "is_relevant": true,
    "search_text": null,
    "facilities": ["wifi", "power-outlet"],
    "min_rating": null,
    "max_rating": null,
    "price_category": "murah",
    "location": "bandung",
    "intent": "kerja",
    "sort_by": null,
    "entity_type": "cafe",
    "limit": null
}

Query: "3 cafe untuk nongkrong"
{
    "is_relevant": true,
    "query_type": "search",
    "search_text": null,
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": "nongkrong",
    "sort_by": null,
    "entity_type": "cafe",
    "limit": 3
}

Query: "5 tempat ngopi murah di jakarta"
{
    "is_relevant": true,
    "query_type": "search",
    "search_text": null,
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": "murah",
    "location": "jakarta",
    "intent": null,
    "sort_by": null,
    "entity_type": "cafe",
    "limit": 5
}

Query: "hello world"
{
    "is_relevant": false,
    "search_text": null,
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": null,
    "sort_by": null,
    "entity_type": "cafe",
    "limit": null
}

Query: "siapa presiden indonesia"
{
    "is_relevant": false,
    "query_type": "irrelevant",
    "search_text": null,
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": null,
    "sort_by": null,
    "entity_type": "cafe",
    "limit": null
}

Query: "kamu siapa?"
{
    "is_relevant": false,
    "query_type": "identity",
    "search_text": null,
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": null,
    "sort_by": null,
    "entity_type": "cafe",
    "limit": null
}

Query: "halo"
{
    "is_relevant": false,
    "query_type": "greeting",
    "search_text": null,
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": null,
    "sort_by": null,
    "entity_type": "cafe",
    "limit": null
}

Query: "siapa yang buat aplikasi ini"
{
    "is_relevant": false,
    "query_type": "creator",
    "search_text": null,
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": null,
    "sort_by": null,
    "entity_type": "cafe",
    "limit": null
}

Query: "tempat nongkrong rating tinggi"
{
    "search_text": null,
    "facilities": [],
    "min_rating": 4.0,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": "nongkrong",
    "sort_by": "rating",
    "entity_type": "cafe",
    "limit": null
}

Query: "collection cafe untuk korporat"
{
    "search_text": "korporat",
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": "meeting",
    "sort_by": null,
    "entity_type": "collection",
    "limit": null
}

Query: "koleksi kafe romantis"
{
    "search_text": "romantis",
    "facilities": [],
    "min_rating": null,
    "max_rating": null,
    "price_category": null,
    "location": null,
    "intent": "kencan",
    "sort_by": null,
    "entity_type": "collection",
    "limit": null
}"""

    def __init__(self):
        self.groq_client = None

        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Groq: {e}")

    def _parse_with_groq(self, query: str) -> ParsedQuery:
        """Parse query using Groq API"""
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast and free
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f'Query: "{query}"'}
            ],
            temperature=0.1,
            max_tokens=500,
        )

        response_text = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = re.sub(r'^```(?:json)?\n?', '', response_text)
            response_text = re.sub(r'\n?```$', '', response_text)

        parsed = json.loads(response_text)
        return ParsedQuery(**parsed)

    def parse_query(self, query: str) -> ParsedQuery:
        """Parse natural language query into structured filters"""
        if not self.groq_client:
            # Fallback: return query as search_text if no Groq configured
            return ParsedQuery(search_text=query)

        try:
            return self._parse_with_groq(query)
        except Exception as e:
            print(f"Groq parse error: {e}")
            return ParsedQuery(search_text=query)

    def search_cafes(
        self,
        db: Session,
        parsed: ParsedQuery,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search cafes based on parsed query"""
        # Use limit from parsed query if available
        if parsed.limit is not None and parsed.limit > 0:
            page_size = min(parsed.limit, 100)  # Cap at 100
            page = 1  # Reset to first page when limit is specified

        query = db.query(Cafe)

        # Apply text search
        if parsed.search_text:
            search_term = f"%{parsed.search_text}%"
            query = query.filter(
                or_(
                    Cafe.nama.ilike(search_term),
                    Cafe.alamat_lengkap.ilike(search_term)
                )
            )

        # Apply location filter
        if parsed.location:
            query = query.filter(Cafe.alamat_lengkap.ilike(f"%{parsed.location}%"))

        # Apply rating filters
        if parsed.min_rating is not None:
            query = query.filter(Cafe.rating >= parsed.min_rating)
        if parsed.max_rating is not None:
            query = query.filter(Cafe.rating <= parsed.max_rating)

        # Apply price category filter
        if parsed.price_category:
            if parsed.price_category == "murah":
                query = query.filter(
                    or_(
                        Cafe.range_price.ilike("%murah%"),
                        Cafe.range_price.ilike("%10.000%"),
                        Cafe.range_price.ilike("%15.000%"),
                        Cafe.range_price.ilike("%20.000%"),
                        Cafe.range_price.ilike("%25.000%"),
                    )
                )
            elif parsed.price_category == "mahal":
                query = query.filter(
                    or_(
                        Cafe.range_price.ilike("%mahal%"),
                        Cafe.range_price.ilike("%100.000%"),
                        Cafe.range_price.ilike("%150.000%"),
                        Cafe.range_price.ilike("%200.000%"),
                    )
                )

        # Apply facility filters
        if parsed.facilities:
            for facility_slug in parsed.facilities:
                query = query.filter(
                    Cafe.facilities.any(Facility.slug == facility_slug)
                )

        # Apply sorting (MySQL compatible - use CASE for NULLS LAST)
        if parsed.sort_by == "rating":
            query = query.order_by(
                case((Cafe.rating.is_(None), 1), else_=0),
                Cafe.rating.desc()
            )
        elif parsed.sort_by == "reviews":
            query = query.order_by(
                case((Cafe.count_google_review.is_(None), 1), else_=0),
                Cafe.count_google_review.desc()
            )
        elif parsed.sort_by == "terbaru":
            query = query.order_by(Cafe.created_at.desc())
        else:
            # Default: sort by rating
            query = query.order_by(
                case((Cafe.rating.is_(None), 1), else_=0),
                Cafe.rating.desc()
            )

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        cafes = query.offset(offset).limit(page_size).all()

        return {
            "items": cafes,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "parsed_query": parsed.model_dump()
        }

    def search_facilities(
        self,
        db: Session,
        parsed: ParsedQuery,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search facilities based on parsed query"""
        # Use limit from parsed query if available
        if parsed.limit is not None and parsed.limit > 0:
            page_size = min(parsed.limit, 100)
            page = 1

        query = db.query(Facility)

        if parsed.search_text:
            search_term = f"%{parsed.search_text}%"
            query = query.filter(
                or_(
                    Facility.name.ilike(search_term),
                    Facility.description.ilike(search_term)
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        facilities = query.offset(offset).limit(page_size).all()

        return {
            "items": facilities,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "parsed_query": parsed.model_dump()
        }

    INTENT_KEYWORDS = {
        "kerja": ["wfh", "work", "kerja", "remote", "coworking", "produktif"],
        "meeting": ["meeting", "corporate", "korporat", "bisnis", "premium", "wfh", "work"],
        "nongkrong": ["hangout", "nongkrong", "santai", "chill", "casual"],
        "foto": ["instagram", "aesthetic", "foto", "instagrammable", "spot"],
        "belajar": ["study", "belajar", "quiet", "tenang", "wfh"],
        "kencan": ["romantic", "date", "kencan", "romantis", "couple"],
    }

    def search_collections(
        self,
        db: Session,
        parsed: ParsedQuery,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search collections based on parsed query"""
        # Use limit from parsed query if available
        if parsed.limit is not None and parsed.limit > 0:
            page_size = min(parsed.limit, 100)
            page = 1

        query = db.query(Collection).filter(Collection.visibility == 'public')

        # Build search conditions
        search_conditions = []

        # Add search_text condition
        if parsed.search_text:
            search_term = f"%{parsed.search_text}%"
            search_conditions.append(Collection.name.ilike(search_term))
            search_conditions.append(Collection.description.ilike(search_term))

        # Add intent-based keywords
        if parsed.intent and parsed.intent in self.INTENT_KEYWORDS:
            for keyword in self.INTENT_KEYWORDS[parsed.intent]:
                search_conditions.append(Collection.name.ilike(f"%{keyword}%"))
                search_conditions.append(Collection.description.ilike(f"%{keyword}%"))

        # Apply OR conditions if any
        if search_conditions:
            query = query.filter(or_(*search_conditions))

        total = query.count()
        offset = (page - 1) * page_size
        collections = query.offset(offset).limit(page_size).all()

        return {
            "items": collections,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "parsed_query": parsed.model_dump()
        }

    def search_all(
        self,
        db: Session,
        query_text: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Universal search across all entities"""
        parsed = self.parse_query(query_text)

        results = {
            "parsed_query": parsed.model_dump(),
            "results": {}
        }

        if parsed.entity_type in ["cafe", "all"]:
            results["results"]["cafes"] = self.search_cafes(db, parsed, page, page_size)

        if parsed.entity_type in ["facility", "all"]:
            results["results"]["facilities"] = self.search_facilities(db, parsed, page, page_size)

        if parsed.entity_type in ["collection", "all"]:
            results["results"]["collections"] = self.search_collections(db, parsed, page, page_size)

        return results


# Singleton instance
nl_search_service = NLSearchService()
