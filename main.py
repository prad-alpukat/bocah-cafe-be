from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import cafe, auth

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bocah Cafe API",
    description="API untuk menampilkan data cafe dari Google Maps",
    version="1.0.0"
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

@app.get("/")
def read_root():
    return {"message": "Welcome to Bocah Cafe API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
