"""
Main FastAPI application for AI-powered trip planner
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from backend.models.db_config import get_db, DatabaseManager
from backend.models.schemas import *
from backend.api.auth import router as auth_router
from backend.api.users import router as users_router
from backend.api.recommendations import router as recommendations_router
from backend.api.swipes import router as swipes_router
from backend.api.groups import router as groups_router
from backend.api.content import router as content_router
from backend.utils.logging_config import setup_logging


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Trip Planner API")
    
    # Initialize database
    try:
        DatabaseManager.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Trip Planner API")


# Create FastAPI app
app = FastAPI(
    title="AI-Powered Trip Planner API",
    description="Swipe-based personalized travel recommendations with AI",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None,
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("DEBUG", "False").lower() == "true" else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if os.getenv("DEBUG", "False").lower() == "true" else ["yourdomain.com", "*.yourdomain.com"]
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(swipes_router, prefix="/api/v1/swipes", tags=["Swipe Interactions"])
app.include_router(groups_router, prefix="/api/v1/groups", tags=["Group Collaboration"])
app.include_router(content_router, prefix="/api/v1/content", tags=["Travel Content"])


# Root endpoints
@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "AI-Powered Trip Planner API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check with database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/v1/stats")
async def get_api_stats(db: Session = Depends(get_db)):
    """Get API usage statistics"""
    try:
        from backend.models.database import User, TravelContent, SwipeInteraction
        
        # Get basic counts
        stats = {
            "total_users": db.query(User).filter(User.is_active == True).count(),
            "total_content": db.query(TravelContent).filter(TravelContent.is_active == True).count(),
            "total_swipes": db.query(SwipeInteraction).count(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API statistics"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "detail": "The requested resource was not found",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error", 
        "detail": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
        log_level="info"
    )
