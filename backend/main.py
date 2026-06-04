from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.database import engine, get_db, Base
from backend.routers import users, enrollment, verification

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Behavioral Biometrics Authentication System")
    yield
    # Shutdown
    logger.info("Shutting down application")

app = FastAPI(
    title="Behavioral Biometrics Continuous Authentication",
    description="ML-powered continuous authentication based on user behavior patterns",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(enrollment.router, prefix="/api/enrollment", tags=["Enrollment"])
app.include_router(verification.router, prefix="/api/verify", tags=["Verification"])

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Behavioral Biometrics Authentication API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Behavioral Biometrics API",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
