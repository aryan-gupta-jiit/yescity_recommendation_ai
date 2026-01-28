import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Add src to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.yescity_recommendation_ai.api.routes import router as api_router
from src.yescity_recommendation_ai.utils.logger import setup_logger
from src.yescity_recommendation_ai.database.mongodb_client import mongodb_client

load_dotenv()

# Setup logger
logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("🚀 Starting YesCity Recommendation API")
    try:
        # Test MongoDB connection
        mongodb_client.db.command("ping")
        logger.info("✅ MongoDB connection established")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down YesCity Recommendation API")
    mongodb_client.close()

# Create FastAPI app
app = FastAPI(
    title="YesCity Travel Recommendation API",
    description="AI-powered travel assistant for India using YesCity3 database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to YesCity Travel Recommendation API",
        "version": "1.0.0",
        "database": "YesCity3",
        "llm": "Ollama (Local)",
        "endpoints": {
            "recommend": "/api/v1/recommend (POST)",
            "category_search": "/api/v1/category-search (POST)",
            "foods": "/api/v1/foods (GET)",
            "health": "/api/v1/health (GET)",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check MongoDB
        mongodb_client.db.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "running",
        "database": db_status,
        "timestamp": "now"  # You can add datetime here
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )