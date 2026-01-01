from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from services.nl_search import nl_search_service, ParsedQuery
from schemas import CafeResponse, FacilityResponse, CollectionResponse, PaginationMeta
from config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class NLSearchRequest(BaseModel):
    """Request body for natural language search"""
    query: str = Field(..., min_length=2, max_length=500, description="Natural language search query")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class CafeSearchResult(BaseModel):
    """Cafe search result with metadata"""
    items: List[CafeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class FacilitySearchResult(BaseModel):
    """Facility search result with metadata"""
    items: List[FacilityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class CollectionSearchResult(BaseModel):
    """Collection search result with metadata"""
    items: List[CollectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    """Combined search results"""
    cafes: Optional[CafeSearchResult] = None
    facilities: Optional[FacilitySearchResult] = None
    collections: Optional[CollectionSearchResult] = None


class NLSearchResponse(BaseModel):
    """Response for natural language search"""
    query: str = Field(..., description="Original query")
    parsed_query: Dict[str, Any] = Field(..., description="Parsed query interpretation")
    results: SearchResults = Field(..., description="Search results by entity type")


class ParseQueryResponse(BaseModel):
    """Response for parse-only endpoint"""
    query: str
    parsed: ParsedQuery


@router.post("/")
@limiter.limit("30/minute")
def natural_language_search(
    request: Request,
    body: NLSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search across all entities using natural language.

    Supports queries like:
    - "kafe dengan wifi di bandung yang murah"
    - "tempat nongkrong rating tinggi"
    - "cafe untuk kerja remote dengan colokan"
    - "meeting room di jakarta"

    The query will be parsed by AI to extract:
    - Facilities (wifi, ac, mushola, etc.)
    - Location
    - Price category (murah/sedang/mahal)
    - Rating requirements
    - Intent (kerja, nongkrong, meeting, etc.)
    """
    if not settings.GROQ_API_KEY and not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Natural language search is not configured. Please set GROQ_API_KEY or GEMINI_API_KEY."
        )

    result = nl_search_service.search_all(
        db=db,
        query_text=body.query,
        page=body.page,
        page_size=body.page_size
    )

    # Check query type and respond accordingly
    query_type = result["parsed_query"].get("query_type", "search")

    if query_type == "identity":
        return {
            "query": body.query,
            "message": "Gw adalah asisten pencari cafe terbaik! 🏪☕ Tanya gw soal cafe, nongkrong, atau tempat ngopi aja ya!",
            "type": "identity"
        }
    elif query_type == "greeting":
        return {
            "query": body.query,
            "message": "Halo juga! 👋 Mau cari cafe apa nih? Kasih tau aja, misal: 'cafe wifi murah di Jakarta'",
            "type": "greeting"
        }
    elif not result["parsed_query"].get("is_relevant", True):
        return {
            "query": body.query,
            "message": "Apasih anjing gaje 😂 Ke gw bahas cafe aja ya!",
            "type": "irrelevant"
        }

    # Transform results to response format
    search_results = SearchResults()

    if "cafes" in result["results"]:
        cafe_data = result["results"]["cafes"]
        search_results.cafes = CafeSearchResult(
            items=[CafeResponse.model_validate(c) for c in cafe_data["items"]],
            total=cafe_data["total"],
            page=cafe_data["page"],
            page_size=cafe_data["page_size"],
            total_pages=cafe_data["total_pages"]
        )

    if "facilities" in result["results"]:
        facility_data = result["results"]["facilities"]
        search_results.facilities = FacilitySearchResult(
            items=[FacilityResponse.model_validate(f) for f in facility_data["items"]],
            total=facility_data["total"],
            page=facility_data["page"],
            page_size=facility_data["page_size"],
            total_pages=facility_data["total_pages"]
        )

    if "collections" in result["results"]:
        collection_data = result["results"]["collections"]
        search_results.collections = CollectionSearchResult(
            items=[
                CollectionResponse(
                    id=c.id,
                    name=c.name,
                    slug=c.slug,
                    description=c.description,
                    gambar_cover=c.gambar_cover,
                    visibility=c.visibility,
                    cafe_count=len(c.cafes),
                    created_at=c.created_at,
                    updated_at=c.updated_at
                )
                for c in collection_data["items"]
            ],
            total=collection_data["total"],
            page=collection_data["page"],
            page_size=collection_data["page_size"],
            total_pages=collection_data["total_pages"]
        )

    return NLSearchResponse(
        query=body.query,
        parsed_query=result["parsed_query"],
        results=search_results
    )


@router.get("/cafes")
@limiter.limit("30/minute")
def search_cafes_nl(
    request: Request,
    q: str = Query(..., min_length=2, max_length=500, description="Natural language search query"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search cafes only using natural language.

    Example queries:
    - "kafe dengan wifi dan ac"
    - "tempat kerja murah di bandung"
    - "cafe rating 4 ke atas"
    """
    if not settings.GROQ_API_KEY and not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Natural language search is not configured. Please set GROQ_API_KEY or GEMINI_API_KEY."
        )

    parsed = nl_search_service.parse_query(q)

    # Check query type and respond accordingly
    if parsed.query_type == "identity":
        return {
            "query": q,
            "message": "Gw adalah asisten pencari cafe terbaik! 🏪☕ Tanya gw soal cafe, nongkrong, atau tempat ngopi aja ya!",
            "type": "identity"
        }
    elif parsed.query_type == "greeting":
        return {
            "query": q,
            "message": "Halo juga! 👋 Mau cari cafe apa nih? Kasih tau aja, misal: 'cafe wifi murah di Jakarta'",
            "type": "greeting"
        }
    elif not parsed.is_relevant:
        return {
            "query": q,
            "message": "Apasih anjing gaje 😂 Ke gw bahas cafe aja ya!",
            "type": "irrelevant"
        }

    result = nl_search_service.search_cafes(db, parsed, page, page_size)

    return {
        "query": q,
        "parsed_query": result["parsed_query"],
        "data": [CafeResponse.model_validate(c) for c in result["items"]],
        "meta": PaginationMeta(
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    }


@router.post("/parse")
@limiter.limit("30/minute")
def parse_query_only(
    request: Request,
    body: NLSearchRequest,
):
    """
    Parse a natural language query without executing search.
    Useful for debugging or understanding how queries are interpreted.
    """
    if not settings.GROQ_API_KEY and not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Natural language search is not configured. Please set GROQ_API_KEY or GEMINI_API_KEY."
        )

    parsed = nl_search_service.parse_query(body.query)

    return ParseQueryResponse(
        query=body.query,
        parsed=parsed
    )


@router.get("/suggestions")
def get_search_suggestions():
    """
    Get example search queries and available filters.
    Useful for UI autocomplete or help text.
    """
    return {
        "example_queries": [
            "kafe dengan wifi di jakarta",
            "tempat nongkrong rating tinggi",
            "cafe murah untuk kerja remote",
            "kafe dengan mushola dan parkir",
            "tempat meeting di bandung",
            "cafe aesthetic untuk foto",
            "coffee shop dengan live music",
        ],
        "available_facilities": [
            {"slug": "wifi", "name": "WiFi"},
            {"slug": "ac", "name": "AC"},
            {"slug": "mushola", "name": "Mushola"},
            {"slug": "toilet", "name": "Toilet"},
            {"slug": "parking", "name": "Parkir"},
            {"slug": "outdoor", "name": "Area Outdoor"},
            {"slug": "indoor", "name": "Area Indoor"},
            {"slug": "smoking-area", "name": "Smoking Area"},
            {"slug": "meeting-room", "name": "Ruang Meeting"},
            {"slug": "power-outlet", "name": "Stop Kontak"},
            {"slug": "pet-friendly", "name": "Pet Friendly"},
            {"slug": "live-music", "name": "Live Music"},
            {"slug": "board-games", "name": "Board Games"},
        ],
        "price_categories": ["murah", "sedang", "mahal"],
        "intents": ["kerja", "nongkrong", "meeting", "foto", "belajar", "kencan"],
        "sort_options": ["rating", "reviews", "terbaru"]
    }
