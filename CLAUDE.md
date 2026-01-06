# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bocah Cafe API - FastAPI backend for a cafe directory application with natural language search powered by Groq AI.

## Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server (http://localhost:8000)
python main.py

# Database seeding
python seed.py              # Run all seeders
python seed.py --fresh      # Drop tables and re-seed
python seed.py --only roles # Seed specific table

# Run migrations
python migrations/<migration_file>.py
python migrations/migrate_facility_icons.py --dry-run  # Preview icon migration
```

## Architecture

### Core Structure
- `main.py` - FastAPI app initialization, router registration, middleware setup
- `config.py` - Pydantic BaseSettings loading from `.env`
- `database.py` - SQLAlchemy engine (SQLite dev / MySQL prod)
- `models.py` - All SQLAlchemy ORM models
- `schemas.py` - Pydantic request/response schemas with validators
- `auth_utils.py` - JWT authentication and role-based access utilities

### API Routers (`/routers/`)
| Prefix | File | Purpose |
|--------|------|---------|
| `/api/auth` | auth.py | Login, register, current user |
| `/api/cafe` | cafe.py | Cafe CRUD with filtering/sorting |
| `/api/admin` | admin.py | Admin management (superadmin only) |
| `/api/roles` | role.py | Role management (superadmin only) |
| `/api/facilities` | facility.py | Facility CRUD + icon upload |
| `/api/collections` | collection.py | Cafe collections with visibility |
| `/api/search` | search.py | Natural language search via Groq |
| `/api/upload` | upload.py | Firebase image upload |

### Database Models
- **Admin** - Users with role FK
- **Role** - System roles (superadmin, writer) + custom roles
- **Cafe** - Cafe data with M2M to Facility and Collection
- **Facility** - Amenities (wifi, ac, parking) with Iconify icons
- **Collection** - Curated cafe lists (public/private/password-protected)

### Key Services
- `services/nl_search.py` - Groq API integration with load balancing for multiple API keys

## Patterns

### Authentication
```python
# Require any authenticated admin
current_admin: Admin = Depends(get_current_admin)

# Require superadmin role
current_admin: Admin = Depends(get_superadmin)
```

### Response Format
All list endpoints return `PaginatedResponse[T]` with:
```json
{
  "data": [...],
  "meta": { "total": 100, "page": 1, "page_size": 10, "total_pages": 10 }
}
```

### Facility Icons
Icons use Iconify format (`iconify:lucide:wifi`) or PNG URLs from allowed domains. Raw SVG is rejected for security.

## Environment Variables

Key settings in `.env`:
- `SECRET_KEY` - JWT secret (min 32 chars for production)
- `DATABASE_URL` - SQLite or MySQL connection string
- `GROQ_API_KEYS` - Comma-separated API keys for load balancing
- `FIREBASE_STORAGE_BUCKET` - Firebase project bucket
- `ALLOW_ADMIN_REGISTRATION` - Set false after initial admin created

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Git Rules

- **JANGAN** sertakan mention AI di commit message (no "Generated with Claude", "Co-Authored-By: Claude", dll)
- Commit message harus natural seperti ditulis developer manusia
