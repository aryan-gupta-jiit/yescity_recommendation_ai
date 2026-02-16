import time
from typing import Dict, List, Any, Optional
from unicodedata import category
from ..database.mongodb_client import mongodb_client
from .query_classifier import query_classifier
# from .crew.crew_manager  import crew_manager
# from yescity_recommendation_ai.crew import crew_manager
from bson import ObjectId

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

class RecommendationService:
    """ Main service to handle recommendation requests """

    def __init__(self):
        from ..crew.crew_manager import crew_manager
        self.crew_manager = crew_manager

    def get_recommendations(self,user_query:str)->Dict[str,Any]:
        """ Get recommendations based on user query """
        start_time = time.time()

        # Step 1: Classify the query
        classification = query_classifier.classify_query(user_query)
        print(f"📊 Classification: {classification.category} in {classification.cityName}")


        # Step 2: Process through crew manager
        crew_result=self.crew_manager.process_query(user_query)

        processing_time = time.time() - start_time
        
        if not crew_result.get("success",False):
            crew_result["processing_time"]=round(processing_time,3)
            return crew_result
        
        # Step 3: Fetch additional data from MongoDB if needed
        recommendations = crew_result.get("recommendations", [])
        category = crew_result.get("category")

        if recommendations and category:
            full_data=self._get_full_data(category,recommendations)
            crew_result["full_data"]=full_data
        
        crew_result["processing_time"]=round(processing_time,3)
        crew_result["classification"] = classification.dict()

        return crew_result
    
    def get_recommendation_by_category(self,category:str,city:str,**filters) -> Dict[str,Any]:
        """
        Direct recommendation by category (for UI buttons).
        
        Args:
            category: Collection name
            city: City name
            **filters: Additional filters
            
        Returns:
            Dictionary with recommendations
        """

        query_parts=[f"{category} in {city}"]
        for key,value in filters.items():
            if value:
                query_parts.append(f"{key}: {value}")

        user_query=" ".join(query_parts)

        # Process through the normal pipeline

        return self.get_recommendations(user_query)
    
    def _get_full_data(self,category:str,recommendations:List[Dict[str,Any]])->List[Dict[str,Any]]:
        """
        Fetch complete data for recommendations from MongoDB.
        
        Args:
            category: Collection name
            recommendations: List of {_id, name} or {_id, foodPlace}
            
        Returns:
            List of complete document data
        """
        full_data=[]
        collection=mongodb_client.get_collection(category)

        for rec in recommendations:
            try:
                doc=None

                # Try to find by _id first
                if "_id" in rec:
                    try:
                        doc=collection.find_one({"_id":ObjectId(rec["_id"])})
                    except:
                        pass

                # If not found by _id, try by name or foodPlace or shops
                if not doc:
                    # Determine the name field based on category
                    if category == "foods":
                        name_field = "foodPlace"
                    elif category == "shoppings":
                        name_field = "shops"
                    else:
                        name_field = "name"

                    search_name = rec.get("name") or rec.get("foodPlace") or rec.get("shops")

                    if search_name:
                        # try exact match first
                        doc=collection.find_one({name_field:search_name})

                        if not doc:
                            # try case-insensitive match
                            doc=collection.find_one({name_field:{"$regex":f"^{search_name}$","$options":"i"}})

                    if doc:
                        # Convert all ObjectId fields to strings recursively
                        doc = convert_objectid_to_str(doc)
                        full_data.append(doc)
                    else:
                        # Add partial data if not found
                        rec["error"]="Document not found in database"
                        full_data.append(rec)

            except Exception as e:
                print(f"Error fetching data:{e}")
                rec["error"] = f"Error fetching data: {str(e)}"
                full_data.append(rec)

        return full_data

# Create singleton instance
recommendation_service = RecommendationService()



        
    

