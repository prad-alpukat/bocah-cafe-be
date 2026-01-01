from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import engine, Base
from routers import cafe, auth, upload, admin, role, facility, collection, search

# Create database tables
Base.metadata.create_all(bind=engine)

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Bocah Cafe API",
    description="API untuk menampilkan data cafe dari Google Maps",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter

# Custom rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Sabar bang, kebanyakan request nih! Coba lagi nanti ya 😅",
            "retry_after": str(exc.detail)
        }
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(cafe.router, prefix="/api/cafe", tags=["Cafe"])
app.include_router(facility.router, prefix="/api/facilities", tags=["Facilities"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Management"])
app.include_router(role.router, prefix="/api/roles", tags=["Role Management"])
app.include_router(collection.router, prefix="/api/collections", tags=["Collections"])
app.include_router(search.router, prefix="/api/search", tags=["Natural Language Search"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Bocah Cafe API"}
