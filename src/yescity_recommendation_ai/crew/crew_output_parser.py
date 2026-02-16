# import json
# import re
# from typing import List, Dict, Any, Optional

# class CrewOutputParser:
#     """Parses crew output to extract recommendation IDs."""
    
#     @staticmethod
#     def parse_food_recommendations(output: str) -> List[Dict[str, str]]:
#         """
#         Parse crew output to extract food recommendation IDs and names.
        
#         Args:
#             output: The raw output string from the crew
            
#         Returns:
#             List of dictionaries with _id and name
#         """
#         try:
#             # Try to find JSON in the output
#             json_pattern = r'\{.*\}'
#             match = re.search(json_pattern, output, re.DOTALL)
            
#             if match:
#                 json_str = match.group()
#                 data = json.loads(json_str)
                
#                 if "recommendations" in data:
#                     recommendations = data["recommendations"]
                    
#                     # Validate each recommendation has _id and name
#                     valid_recs = []
#                     for rec in recommendations:
#                         if "_id" in rec and "name" in rec:
#                             valid_recs.append({
#                                 "_id": str(rec["_id"]),
#                                 "name": rec["name"]
#                             })
                    
#                     return valid_recs
            
#             # If JSON parsing fails, try to extract manually
#             return CrewOutputParser._extract_from_text(output)
            
#         except (json.JSONDecodeError, KeyError) as e:
#             print(f"Error parsing crew output: {e}")
#             return CrewOutputParser._extract_from_text(output)
    
#     @staticmethod
#     def _extract_from_text(output: str) -> List[Dict[str, str]]:
#         """Extract recommendations from text when JSON parsing fails."""
#         recommendations = []
        
#         # Look for patterns like "_id: abc123, name: Restaurant Name"
#         pattern = r'_id[:\s]+([^\s,]+)[,\s]+name[:\s]+([^\n]+)'
#         matches = re.findall(pattern, output, re.IGNORECASE)
        
#         for match in matches:
#             _id, name = match
#             recommendations.append({
#                 "_id": _id.strip(),
#                 "name": name.strip()
#             })
#         return recommendations
    
#     @staticmethod
#     def parse_shopping_recommendations(output: str) -> List[Dict[str, str]]:
#         """
#         Parse crew output to extract shopping recommendation IDs and shop names.
        
#         Args:
#             output: The raw output string from the crew
            
#         Returns:
#             List of dictionaries with _id and shops
#         """
#         try:
#             # Try to find JSON in the output
#             json_pattern = r'\{.*\}'
#             match = re.search(json_pattern, output, re.DOTALL)
            
#             if match:
#                 json_str = match.group()
#                 data = json.loads(json_str)
                
#                 if "recommendations" in data:
#                     recommendations = data["recommendations"]
                    
#                     # Validate each recommendation has _id and shops
#                     valid_recs = []
#                     for rec in recommendations:
#                         if "_id" in rec and "shops" in rec:
#                             valid_recs.append({
#                                 "_id": str(rec["_id"]),
#                                 "shops": rec["shops"]
#                             })
                    
#                     return valid_recs
            
#             # If JSON parsing fails, try to extract manually
#             return CrewOutputParser._extract_shopping_from_text(output)
            
#         except (json.JSONDecodeError, KeyError) as e:
#             print(f"Error parsing crew output: {e}")
#             return CrewOutputParser._extract_shopping_from_text(output)
    
#     @staticmethod
#     def _extract_shopping_from_text(output: str) -> List[Dict[str, str]]:
#         """Extract shopping recommendations from text when JSON parsing fails."""
#         recommendations = []
        
#         # Look for patterns like "_id: abc123, shops: Shop Name"
#         pattern = r'_id[:\s]+([^\s,]+)[,\s]+shops[:\s]+([^\n]+)'
#         matches = re.findall(pattern, output, re.IGNORECASE)
        
#         for match in matches:
#             _id, shops = match
#             recommendations.append({
#                 "_id": _id.strip(),
#                 "shops": shops.strip()
#             })
        
#         return recommendations

    
#     @staticmethod
#     def format_for_display(recommendations: List[Dict[str, str]]) -> str:
#         """Format recommendations for display."""
#         if not recommendations:
#             return "No recommendations found."
        
#         result = "Recommended Places:\n"
#         for i, rec in enumerate(recommendations, 1):
#             result += f"{i}. {rec['name']} (ID: {rec['_id']})\n"
        
#         return result
import json
import re
from typing import List, Dict, Any

class CrewOutputParser:
    """Parses crew output to extract recommendation IDs."""
    
    @staticmethod
    def parse_shopping_recommendations(output: str) -> List[Dict[str, str]]:
        """
        Parse crew output to extract shopping recommendation IDs and shop names.
        """
        try:
            print(f"Raw output to parse: {output[:200]}...")  # Log first 200 chars
            
            # Try multiple approaches to extract JSON
            
            # Approach 1: Find JSON object pattern
            json_pattern = r'(\{.*"recommendations".*\})'
            match = re.search(json_pattern, output, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                # Clean up the string
                json_str = re.sub(r'[\n\r\t]', '', json_str)
                json_str = re.sub(r'\s+', ' ', json_str)
                
                try:
                    data = json.loads(json_str)
                    if "recommendations" in data and isinstance(data["recommendations"], list):
                        valid_recs = []
                        for rec in data["recommendations"]:
                            if "_id" in rec and "shops" in rec:
                                valid_recs.append({
                                    "_id": str(rec["_id"]),
                                    "shops": rec["shops"]
                                })
                        print(f"✅ Parsed {len(valid_recs)} recommendations via JSON")
                        return valid_recs
                except json.JSONDecodeError:
                    pass
            
            # Approach 2: Look for the exact pattern with _id and shops
            pattern = r'_id["\']?\s*:\s*["\']?([a-f0-9]+)["\']?[\s,]+shops["\']?\s*:\s*["\']([^"\']+)["\']'
            matches = re.findall(pattern, output, re.IGNORECASE)
            
            if matches:
                recommendations = []
                for _id, shops in matches:
                    recommendations.append({
                        "_id": _id.strip(),
                        "shops": shops.strip()
                    })
                print(f"✅ Parsed {len(recommendations)} recommendations via regex")
                return recommendations
            
            # Approach 3: If we got here, no recommendations found
            print("⚠️ No valid recommendations found in output")
            return []
            
        except Exception as e:
            print(f"❌ Error parsing crew output: {e}")
            return []