# from typing import Optional, Dict, Any, List
# from pydantic import Field, BaseModel, ConfigDict
# from crewai.tools import BaseTool
# from .base_tool import MongoDBQueryTool
# from ..database.mongodb_client import mongodb_client


# class ShoppingSearchInput(BaseModel):
#     model_config = ConfigDict(
#         arbitrary_types_allowed=True,
#         populate_by_name=True,
#     )
#     cityName: str = Field(..., description="City name to search for shopping places")
#     category: Optional[str] = Field(None, description="Shopping category to filter by")
#     flagship: Optional[bool] = Field(None, description="Filter for flagship places")
#     maxResults: int = Field(10, description="Maximum number of results to return")


# class ShoppingSearchTool(BaseTool):
#     name: str = "search_shopping_places"
#     description: str = """
#     Search for shopping recommendations in a specific city using YesCity3 database.
#     This tool queries the 'shoppings' collection which contains detailed information
#     about shops, markets, and shopping destinations.
#     """

#     args_schema: type = ShoppingSearchInput

#     def _run(
#             self,
#             cityName: str,
#             category: Optional[str] = None,
#             flagship: Optional[bool] = None,
#             maxResults: int = 10
#     ) -> List[Dict[str, Any]]:
#         query_filter = {"cityName": {"$regex": f"^{cityName}$", "$options": "i"}}

#         if category:
#             query_filter["category"] = {"$regex": category, "$options": "i"}

#         if flagship is not None:
#             query_filter["flagship"] = flagship

#         print(f"🛍️ Searching shoppings in {cityName} with filter: {query_filter}")

#         base_tool = MongoDBQueryTool(collection_name="shoppings")
#         results = base_tool._run(query_filter=query_filter, limit=maxResults)

#         formatted_results = []
#         for result in results:
#             formatted = {
#                 "_id": result.get("_id", ""),
#                 "shops": result.get("shops", "Unknown"),
#                 "cityName": result.get("cityName", ""),
#                 "address": result.get("address", "Address not available"),
#                 "famousFor": result.get("famousFor", "No description"),
#                 "priceRange": result.get("priceRange", "Price not available"),
#                 "flagship": result.get("flagship", False),
#                 "openDay": result.get("openDay", "Days not available"),
#                 "openTime": result.get("openTime", "Timings not available"),
#                 "phone": result.get("phone", "Not available"),
#                 "website": result.get("website", "Not available"),
#                 "locationLink": result.get("locationLink", ""),
#                 "images": result.get("images", []),
#                 "engagement": result.get("engagement", {}),
#                 "reviews": result.get("reviews", []),
#                 "premium": result.get("premium", "FREE")
#             }

#             formatted_results.append(formatted)

#         print(f"✅ Found {len(formatted_results)} shopping places")
#         return formatted_results


# # Create an instance for easy import
# shopping_search_tool = ShoppingSearchTool()

from typing import Optional, Dict, Any, List
from pydantic import Field, BaseModel, ConfigDict, field_validator
from crewai.tools import BaseTool
from .base_tool import MongoDBQueryTool

class ShoppingSearchInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    cityName: str = Field(..., description="City name to search for shopping places")
    category: Optional[str] = Field(None, description="Shopping category to filter by")
    flagship: Optional[bool] = Field(None, description="Filter for flagship places")
    maxResults: int = Field(50, description="Maximum number of results to return")
    
    @field_validator('flagship', mode='before')
    @classmethod
    def validate_flagship(cls, v):
        """Handle string 'null' and convert to None"""
        if v == 'null' or v == 'None' or v is None:
            return None
        if isinstance(v, str):
            return v.lower() == 'true'
        return v

class ShoppingSearchTool(BaseTool):
    name: str = "search_shopping_places"
    description: str = """
    Search for ALL shopping places in a specific city using YesCity3 database.
    This tool returns complete data for all shops in the specified city.
    The agent will then analyze and filter based on user requirements.
    """

    args_schema: type = ShoppingSearchInput

    def _run(
            self,
            cityName: str,
            category: Optional[str] = None,
            flagship: Optional[bool] = None,
            maxResults: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch ALL shopping places in the specified city.
        No filtering - return complete data for agent to analyze.
        """
        
        # Build query filter - only filter by city
        query_filter = {"cityName": {"$regex": f"^{cityName}$", "$options": "i"}}
        
        # Only add category if provided and not 'null'
        if category and category != 'null' and category.lower() != 'none':
            query_filter["category"] = {"$regex": category, "$options": "i"}
        
        # Only add flagship if provided as boolean
        if flagship is not None:
            query_filter["flagship"] = flagship
        
        print(f"🛍️ Fetching shopping places in {cityName} with filter: {query_filter}")
        
        # Get shops in the city
        base_tool = MongoDBQueryTool(collection_name="shoppings")
        all_results = base_tool._run(query_filter=query_filter, limit=maxResults)
        
        # Format results with all fields preserved
        formatted_results = []
        for result in all_results:
            # Keep ALL original fields, just ensure _id is string
            formatted = {
                "_id": str(result.get("_id", "")),
                "cityName": result.get("cityName", ""),
                "shops": result.get("shops", "Unknown"),
                "famousFor": result.get("famousFor", ""),
                "priceRange": result.get("priceRange", ""),
                "flagship": result.get("flagship", False),
                "premium": result.get("premium", "FREE"),
                "address": result.get("address", ""),
                "locationLink": result.get("locationLink", ""),
                "openDay": result.get("openDay", ""),
                "openTime": result.get("openTime", ""),
                "phone": result.get("phone", ""),
                "website": result.get("website", ""),
                "images": result.get("images", []),
                "engagement": result.get("engagement", {}),
                "reviews": result.get("reviews", []),
                "lat": result.get("lat"),
                "lon": result.get("lon"),
                "__v": result.get("__v", 0)
            }
            formatted_results.append(formatted)
        
        print(f"✅ Found {len(formatted_results)} shopping places in {cityName}")
        return formatted_results

shopping_search_tool = ShoppingSearchTool()