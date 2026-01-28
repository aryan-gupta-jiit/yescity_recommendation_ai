from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class RecommendationItem(BaseModel):
    """Individual recommendation item."""
    _id: str
    name: str
    type: Optional[str] = None
    category: Optional[str] = None
    score: Optional[float] = None

class RecommendationResponse(BaseModel):
    """Response schema for recommendations."""
    success: bool
    message: str
    category: str
    city: Optional[str] = None
    parameters: Dict[str, str] = Field(default_factory=dict)
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    full_data: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserQueryRequest(BaseModel):
    """Request schema for natural language queries."""
    query: str = Field(..., min_length=1, description="Natural language query from user")
    user_id: Optional[str] = Field(None, description="Optional user identifier for personalization")
    session_id: Optional[str] = Field(None, description="Optional session identifier")

class CategoryQueryRequest(BaseModel):
    """Request schema for category-based queries (from UI buttons)."""
    category: str = Field(..., description="Category like food, accommodation, etc.")
    city: str = Field(..., description="City name")
    filters: Dict[str, str] = Field(default_factory=dict, description="Additional filters")

class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    database: bool
    gemini_api: bool
    timestamp: datetime = Field(default_factory=datetime.now)