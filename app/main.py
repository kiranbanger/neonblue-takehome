"""
Main FastAPI application for the experimentation platform
"""
from fastapi import FastAPI
from app.models import Base
from app.database import engine
from app.routers import experiments_router, events_router

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Experimentation Platform API",
    description="A simplified A/B testing API service",
    version="1.0.0"
)

# Include routers
app.include_router(experiments_router)
app.include_router(events_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Experimentation Platform API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

