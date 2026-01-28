import time
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from bson import ObjectId

from .schemas import (
    UserQueryRequest, 
    CategoryQueryRequest,
    RecommendationResponse,
    ErrorResponse,
    HealthCheckResponse
)
from ..services.recommendation_service import recommendation_service
from ..services.query_classifier import query_classifier
from ..database.mongodb_client import mongodb_client
from ..utils.logger import logger

router = APIRouter()

def convert_objectid_to_str(data: Any) -> Any:
    """
    Recursively convert all ObjectId instances to strings in nested structures.
    
    Args:
        data: Any data structure (dict, list, ObjectId, or primitive)
        
    Returns:
        The same structure with all ObjectId instances converted to strings
    """
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    else:
        return data

@router.post("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations(request: UserQueryRequest):
    """
    Get travel recommendations based on natural language query.
    Uses Ollama for query classification and CrewAI for recommendations.
    """
    logger.info(f"📝 Processing query: {request.query}")
    start_time = time.time()
    
    try:
        result = recommendation_service.get_recommendations(request.query)
        processing_time = time.time() - start_time
        
        if result.get("success"):
            response = RecommendationResponse(
                success=True,
                message="Recommendations retrieved successfully",
                category=result.get("category", "unknown"),
                city=result.get("city"),
                parameters=result.get("parameters", {}),
                recommendations=[
                    {
                        "_id": rec["_id"],
                        "name": rec["name"],
                        "type": result.get("category")
                    }
                    for rec in result.get("recommendations", [])
                ],
                full_data=result.get("full_data", []),
                processing_time=round(processing_time, 3)
            )
            logger.info(f"✅ Processed in {processing_time:.3f}s - Found {len(response.recommendations)} items")
            return response
        else:
            logger.warning(f"❌ Failed: {result.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error=result.get("error", "Unknown error")
                ).dict()
            )
            
    except Exception as e:
        logger.error(f"💥 Error: {str(e)}")
        error_response = ErrorResponse(
            error=f"Internal server error: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "success": error_response.success,
                "error": error_response.error,
                "details": error_response.details,
                "timestamp": error_response.timestamp.isoformat()
            }
        )

@router.post("/category-search", response_model=RecommendationResponse, tags=["Recommendations"])
async def category_search(request: CategoryQueryRequest):
    """
    Get recommendations by category (for UI buttons).
    Example: {"category": "foods", "city": "Agra", "filters": {"category": "Sweets"}}
    """
    logger.info(f"🔍 Category search: {request.category} in {request.city}")
    start_time = time.time()
    
    try:
        result = recommendation_service.get_recommendations_by_category(
            category=request.category,
            city=request.city,
            **request.filters
        )
        
        processing_time = time.time() - start_time
        
        if result.get("success"):
            response = RecommendationResponse(
                success=True,
                message=f"{request.category.capitalize()} recommendations retrieved",
                category=request.category,
                city=request.city,
                parameters=request.filters,
                recommendations=[
                    {
                        "_id": rec["_id"],
                        "name": rec["name"],
                        "type": request.category
                    }
                    for rec in result.get("recommendations", [])
                ],
                full_data=result.get("full_data", []),
                processing_time=round(processing_time, 3)
            )
            return response
        else:
            raise HTTPException(
                status_code=501 if "not implemented" in result.get("error", "").lower() else 400,
                detail=ErrorResponse(
                    error=result.get("error", "Unknown error")
                ).dict()
            )
            
    except Exception as e:
        logger.error(f"💥 Category search error: {str(e)}")
        error_response = ErrorResponse(
            error=f"Internal server error: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "success": error_response.success,
                "error": error_response.error,
                "details": error_response.details,
                "timestamp": error_response.timestamp.isoformat()
            }
        )

@router.get("/foods", tags=["Data Access"])
async def get_foods(
    city: Optional[str] = Query(None, description="Filter by city"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """Direct access to foods collection with filtering."""
    try:
        collection = mongodb_client.get_foods_collection()
        query = {}
        
        if city:
            query["cityName"] = {"$regex": city, "$options": "i"}
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
        
        cursor = collection.find(query).skip(skip).limit(limit)
        results = list(cursor)
        
        # Convert all ObjectId fields to strings recursively
        results = convert_objectid_to_str(results)
        
        return {
            "success": True,
            "count": len(results),
            "total": collection.count_documents(query),
            "filters": {"city": city, "category": category},
            "data": results
        }
        
    except Exception as e:
        error_response = ErrorResponse(
            error=f"Error accessing foods: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "success": error_response.success,
                "error": error_response.error,
                "details": error_response.details,
                "timestamp": error_response.timestamp.isoformat()
            }
        )

@router.get("/foods/{food_id}", tags=["Data Access"])
async def get_food_by_id(food_id: str):
    """Get specific food document by ID."""
    try:
        collection = mongodb_client.get_foods_collection()
        
        # Try to find by ObjectId
        try:
            doc = collection.find_one({"_id": ObjectId(food_id)})
        except:
            doc = None
        
        # If not found by ObjectId, try by foodPlace name
        if not doc:
            doc = collection.find_one({"foodPlace": {"$regex": f"^{food_id}$", "$options": "i"}})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Food place not found")
        
        # Convert all ObjectId fields to strings recursively
        doc = convert_objectid_to_str(doc)
        
        return {
            "success": True,
            "data": doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_response = ErrorResponse(
            error=f"Error fetching food: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "success": error_response.success,
                "error": error_response.error,
                "details": error_response.details,
                "timestamp": error_response.timestamp.isoformat()
            }
        )

@router.get("/cities", tags=["Utilities"])
async def get_cities():
    """Get all unique cities from foods collection."""
    try:
        collection = mongodb_client.get_foods_collection()
        
        pipeline = [
            {"$group": {"_id": "$cityName"}},
            {"$sort": {"_id": 1}},
            {"$limit": 50}
        ]
        
        results = list(collection.aggregate(pipeline))
        cities = [doc["_id"] for doc in results if doc.get("_id")]
        
        return {
            "success": True,
            "count": len(cities),
            "cities": cities
        }
        
    except Exception as e:
        error_response = ErrorResponse(
            error=f"Error fetching cities: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "success": error_response.success,
                "error": error_response.error,
                "details": error_response.details,
                "timestamp": error_response.timestamp.isoformat()
            }
        )

@router.get("/categories", tags=["Utilities"])
async def get_categories():
    """Get all unique categories from foods collection."""
    try:
        collection = mongodb_client.get_foods_collection()
        
        pipeline = [
            {"$group": {"_id": "$category"}},
            {"$sort": {"_id": 1}},
            {"$limit": 50}
        ]
        
        results = list(collection.aggregate(pipeline))
        categories = [doc["_id"] for doc in results if doc.get("_id")]
        
        return {
            "success": True,
            "count": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        error_response = ErrorResponse(
            error=f"Error fetching categories: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "success": error_response.success,
                "error": error_response.error,
                "details": error_response.details,
                "timestamp": error_response.timestamp.isoformat()
            }
        )

@router.get("/classify", tags=["Utilities"])
async def classify_query(query: str = Query(..., min_length=2)):
    """Classify a query using Ollama."""
    try:
        classification = query_classifier.classify_query(query)
        return {
            "query": query,
            "classification": classification.dict()
        }
    except Exception as e:
        error_response = ErrorResponse(
            error=f"Error classifying query: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "success": error_response.success,
                "error": error_response.error,
                "details": error_response.details,
                "timestamp": error_response.timestamp.isoformat()
            }
        )

@router.get("/health/detailed", tags=["Monitoring"])
async def detailed_health_check():
    """Detailed health check with all dependencies."""
    health_info = {
        "api": "running",
        "timestamp": "now",
        "dependencies": {}
    }
    
    try:
        # Check MongoDB
        mongodb_client.db.command("ping")
        health_info["dependencies"]["mongodb"] = {
            "status": "healthy",
            "database": mongodb_client.db.name,
            "collections": len(mongodb_client.db.list_collection_names())
        }
    except Exception as e:
        health_info["dependencies"]["mongodb"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    try:
        # Check Ollama
        classification = query_classifier.classify_query("test")
        health_info["dependencies"]["ollama"] = {
            "status": "healthy",
            "model": query_classifier.llm.model
        }
    except Exception as e:
        health_info["dependencies"]["ollama"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Overall status
    all_healthy = all(
        dep["status"] == "healthy" 
        for dep in health_info["dependencies"].values()
    )
    health_info["overall"] = "healthy" if all_healthy else "degraded"
    
    return health_info