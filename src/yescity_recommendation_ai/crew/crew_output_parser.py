import json
import re
from typing import List, Dict, Any, Optional

class CrewOutputParser:
    """Parses crew output to extract recommendation IDs."""
    
    @staticmethod
    def parse_food_recommendations(output: str) -> List[Dict[str, str]]:
        """
        Parse crew output to extract food recommendation IDs and names.
        
        Args:
            output: The raw output string from the crew
            
        Returns:
            List of dictionaries with _id and name
        """
        try:
            # Try to find JSON in the output
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, output, re.DOTALL)
            
            if match:
                json_str = match.group()
                data = json.loads(json_str)
                
                if "recommendations" in data:
                    recommendations = data["recommendations"]
                    
                    # Validate each recommendation has _id and name
                    valid_recs = []
                    for rec in recommendations:
                        if "_id" in rec and "name" in rec:
                            valid_recs.append({
                                "_id": str(rec["_id"]),
                                "name": rec["name"]
                            })
                    
                    return valid_recs
            
            # If JSON parsing fails, try to extract manually
            return CrewOutputParser._extract_from_text(output)
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing crew output: {e}")
            return CrewOutputParser._extract_from_text(output)
    
    @staticmethod
    def _extract_from_text(output: str) -> List[Dict[str, str]]:
        """Extract recommendations from text when JSON parsing fails."""
        recommendations = []
        
        # Look for patterns like "_id: abc123, name: Restaurant Name"
        pattern = r'_id[:\s]+([^\s,]+)[,\s]+name[:\s]+([^\n]+)'
        matches = re.findall(pattern, output, re.IGNORECASE)
        
        for match in matches:
            _id, name = match
            recommendations.append({
                "_id": _id.strip(),
                "name": name.strip()
            })
        
        return recommendations
    
    @staticmethod
    def format_for_display(recommendations: List[Dict[str, str]]) -> str:
        """Format recommendations for display."""
        if not recommendations:
            return "No recommendations found."
        
        result = "Recommended Places:\n"
        for i, rec in enumerate(recommendations, 1):
            result += f"{i}. {rec['name']} (ID: {rec['_id']})\n"
        
        return result