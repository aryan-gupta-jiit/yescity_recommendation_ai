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
# import json
# import re
# from typing import List, Dict, Any

# class CrewOutputParser:
#     """Parses crew output to extract recommendation IDs."""
    
#     @staticmethod
#     def parse_shopping_recommendations(output: str) -> List[Dict[str, str]]:
#         """
#         Parse crew output to extract shopping recommendation IDs and shop names.
#         """
#         try:
#             print(f"🔍 Raw output to parse (first 300 chars): {output[:300]}...")
            
#             # Clean the output string first
#             cleaned_output = output.strip()
            
#             # Approach 1: Try to find and parse JSON array or object with recommendations
#             # Look for { ... "recommendations": [...] ... } pattern
#             json_match = re.search(r'\{[^{}]*"recommendations"[^{}]*\[[^\]]*\][^{}]*\}', cleaned_output, re.DOTALL)
            
#             if json_match:
#                 try:
#                     json_str = json_match.group(0)
#                     # Remove all newlines and extra whitespace
#                     json_str = ' '.join(json_str.split())
#                     print(f"📝 Attempting to parse JSON: {json_str[:200]}...")
                    
#                     data = json.loads(json_str)
#                     if "recommendations" in data and isinstance(data["recommendations"], list):
#                         valid_recs = []
#                         for rec in data["recommendations"]:
#                             if isinstance(rec, dict) and "_id" in rec and "shops" in rec:
#                                 valid_recs.append({
#                                     "_id": str(rec["_id"]).strip(),
#                                     "shops": str(rec["shops"]).strip()
#                                 })
                        
#                         if valid_recs:
#                             print(f"✅ Successfully parsed {len(valid_recs)} recommendations via JSON")
#                             return valid_recs
#                 except (json.JSONDecodeError, ValueError) as e:
#                     print(f"⚠️ JSON parsing failed: {e}")
            
#             # Approach 2: Look for individual _id and shops pairs using regex
#             # Pattern to match: "_id": "value", "shops": "value" or similar variations
#             pattern = r'"_id"\s*:\s*"([^"]+)"\s*,\s*"shops"\s*:\s*"([^"]+)"'
#             matches = re.findall(pattern, cleaned_output, re.IGNORECASE)
            
#             if matches:
#                 recommendations = []
#                 for _id, shops in matches:
#                     recommendations.append({
#                         "_id": _id.strip(),
#                         "shops": shops.strip()
#                     })
#                 print(f"✅ Parsed {len(recommendations)} recommendations via regex pattern matching")
#                 return recommendations
            
#             # Approach 3: Try a more lenient pattern without quotes requirement
#             pattern2 = r'_id["\']?\s*:\s*["\']?([a-f0-9]{24})["\']?\s*,?\s*shops["\']?\s*:\s*["\']?([^,\n\r}]+)'
#             matches2 = re.findall(pattern2, cleaned_output, re.IGNORECASE)
            
#             if matches2:
#                 recommendations = []
#                 for _id, shops in matches2:
#                     recommendations.append({
#                         "_id": _id.strip().strip('"').strip("'"),
#                         "shops": shops.strip().strip('"').strip("'")
#                     })
#                 print(f"✅ Parsed {len(recommendations)} recommendations via lenient regex")
#                 return recommendations
            
#             # If we got here, no recommendations found
#             print("⚠️ No valid recommendations found in output")
#             print(f"📄 Full output for debugging:\n{cleaned_output}")
#             return []
            
#         except Exception as e:
#             print(f"❌ Error parsing crew output: {type(e).__name__}: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return []
    
#     @staticmethod
#     def parse_food_recommendations(output: str) -> List[Dict[str, str]]:
#         """
#         Parse crew output to extract food recommendation IDs and names.
#         """
#         try:
#             print(f"🔍 Raw food output to parse (first 300 chars): {output[:300]}...")
            
#             # Clean the output string first
#             cleaned_output = output.strip()
            
#             # Approach 1: Try to find and parse JSON array or object with recommendations
#             json_match = re.search(r'\{[^{}]*"recommendations"[^{}]*\[[^\]]*\][^{}]*\}', cleaned_output, re.DOTALL)
            
#             if json_match:
#                 try:
#                     json_str = json_match.group(0)
#                     # Remove all newlines and extra whitespace
#                     json_str = ' '.join(json_str.split())
#                     print(f"📝 Attempting to parse JSON: {json_str[:200]}...")
                    
#                     data = json.loads(json_str)
#                     if "recommendations" in data and isinstance(data["recommendations"], list):
#                         valid_recs = []
#                         for rec in data["recommendations"]:
#                             # For food, we look for "name" or "foodPlace" field
#                             if isinstance(rec, dict) and "_id" in rec:
#                                 name = rec.get("name") or rec.get("foodPlace") or "Unknown"
#                                 valid_recs.append({
#                                     "_id": str(rec["_id"]).strip(),
#                                     "name": str(name).strip()
#                                 })
                        
#                         if valid_recs:
#                             print(f"✅ Successfully parsed {len(valid_recs)} food recommendations via JSON")
#                             return valid_recs
#                 except (json.JSONDecodeError, ValueError) as e:
#                     print(f"⚠️ JSON parsing failed: {e}")
            
#             # Approach 2: Look for individual _id and name/foodPlace pairs using regex
#             pattern = r'"_id"\s*:\s*"([^"]+)"\s*,\s*"(?:name|foodPlace)"\s*:\s*"([^"]+)"'
#             matches = re.findall(pattern, cleaned_output, re.IGNORECASE)
            
#             if matches:
#                 recommendations = []
#                 for _id, name in matches:
#                     recommendations.append({
#                         "_id": _id.strip(),
#                         "name": name.strip()
#                     })
#                 print(f"✅ Parsed {len(recommendations)} food recommendations via regex pattern matching")
#                 return recommendations
            
#             # Approach 3: Try a more lenient pattern
#             pattern2 = r'_id["\']?\s*:\s*["\']?([a-f0-9]{24})["\']?\s*,?\s*(?:name|foodPlace)["\']?\s*:\s*["\']?([^,\n\r}]+)'
#             matches2 = re.findall(pattern2, cleaned_output, re.IGNORECASE)
            
#             if matches2:
#                 recommendations = []
#                 for _id, name in matches2:
#                     recommendations.append({
#                         "_id": _id.strip().strip('"').strip("'"),
#                         "name": name.strip().strip('"').strip("'")
#                     })
#                 print(f"✅ Parsed {len(recommendations)} food recommendations via lenient regex")
#                 return recommendations
            
#             # If we got here, no recommendations found
#             print("⚠️ No valid food recommendations found in output")
#             print(f"📄 Full output for debugging:\n{cleaned_output}")
#             return []
            
#         except Exception as e:
#             print(f"❌ Error parsing crew output: {type(e).__name__}: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return []

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
            print("="*50)
            print("PARSER DEBUG - START")
            print(f"Raw output type: {type(output)}")
            print(f"Raw output length: {len(output)}")
            print(f"Raw output repr (first 200 chars): {repr(output[:200])}")
            print(f"Raw output repr (last 200 chars): {repr(output[-200:])}")
            
            # Convert to string if it's not already
            output_str = str(output)
            
            # Try multiple approaches to find JSON
            
            # Approach 1: Look for anything that looks like a JSON object
            # Find the first { and last }
            first_brace = output_str.find('{')
            last_brace = output_str.rfind('}')
            
            print(f"First brace at position: {first_brace}")
            print(f"Last brace at position: {last_brace}")
            
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_candidate = output_str[first_brace:last_brace + 1]
                print(f"JSON candidate (first 200): {repr(json_candidate[:200])}")
                
                # Try to parse it
                try:
                    data = json.loads(json_candidate)
                    print(f"✅ Successfully parsed JSON: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"JSON keys: {list(data.keys())}")
                        
                        if "recommendations" in data:
                            recs = data["recommendations"]
                            print(f"Recommendations type: {type(recs)}")
                            print(f"Recommendations count: {len(recs) if isinstance(recs, list) else 'not a list'}")
                            
                            if isinstance(recs, list):
                                valid_recs = []
                                for i, rec in enumerate(recs):
                                    print(f"Rec {i}: {rec}")
                                    if isinstance(rec, dict) and "_id" in rec and "shops" in rec:
                                        valid_recs.append({
                                            "_id": str(rec["_id"]).strip(),
                                            "shops": str(rec["shops"]).strip()
                                        })
                                print(f"✅ Found {len(valid_recs)} valid recommendations")
                                return valid_recs
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
            
            # Approach 2: Look for the pattern with _id and shops
            print("\nTrying regex approach...")
            pattern = r'_id["\']?\s*:\s*["\']?([a-f0-9]{24})["\']?\s*,?\s*shops["\']?\s*:\s*["\']?([^,\n\r}]+)'
            matches = re.findall(pattern, output_str, re.IGNORECASE)
            print(f"Regex matches: {matches}")
            
            if matches:
                recommendations = []
                for _id, shops in matches:
                    recommendations.append({
                        "_id": _id.strip(),
                        "shops": shops.strip()
                    })
                print(f"✅ Found {len(recommendations)} recommendations via regex")
                return recommendations
            
            # Approach 3: Look for any 24-char hex strings near the error
            print("\nTrying ID extraction...")
            id_pattern = r'[a-f0-9]{24}'
            ids = re.findall(id_pattern, output_str)
            print(f"Found IDs: {ids}")
            
            # Look for quoted strings that might be shop names
            shop_pattern = r'"([^"]{3,})"'  # Quoted strings at least 3 chars
            shops = re.findall(shop_pattern, output_str)
            print(f"Found quoted strings: {shops[:5]}")
            
            print("PARSER DEBUG - END")
            print("="*50)
            
            return []
            
        except Exception as e:
            print(f"❌ Error in parser: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    # @staticmethod
    # def parse_shopping_recommendations(output: str) -> List[Dict[str, str]]:
    #     """
    #     Parse crew output to extract shopping recommendation IDs and shop names.
    #     """
    #     try:
    #         print(f"🔍 Raw output to parse: {repr(output[:500])}...")
            
    #         # Step 1: Clean the output aggressively
    #         # Remove any leading/trailing whitespace and newlines
    #         cleaned = output.strip()
            
    #         # Remove any markdown code block markers
    #         cleaned = re.sub(r'```json\s*', '', cleaned)
    #         cleaned = re.sub(r'```\s*', '', cleaned)
            
    #         # Remove any text before the first {
    #         first_brace = cleaned.find('{')
    #         if first_brace > 0:
    #             cleaned = cleaned[first_brace:]
    #             print(f"📝 Removed text before JSON: {cleaned[:100]}...")
            
    #         # Remove any text after the last }
    #         last_brace = cleaned.rfind('}')
    #         if last_brace > 0 and last_brace < len(cleaned) - 1:
    #             cleaned = cleaned[:last_brace + 1]
    #             print(f"📝 Removed text after JSON: {cleaned[:100]}...")
            
    #         # Step 2: Try to parse as JSON
    #         try:
    #             data = json.loads(cleaned)
    #             print(f"✅ Successfully parsed JSON directly")
                
    #             if isinstance(data, dict) and "recommendations" in data:
    #                 recommendations = data["recommendations"]
    #                 if isinstance(recommendations, list):
    #                     valid_recs = []
    #                     for rec in recommendations:
    #                         if isinstance(rec, dict) and "_id" in rec and "shops" in rec:
    #                             valid_recs.append({
    #                                 "_id": str(rec["_id"]).strip(),
    #                                 "shops": str(rec["shops"]).strip()
    #                             })
    #                     print(f"✅ Found {len(valid_recs)} valid recommendations")
    #                     return valid_recs
    #         except json.JSONDecodeError as e:
    #             print(f"⚠️ Direct JSON parsing failed: {e}")
            
    #         # Step 3: If direct parsing fails, try to extract JSON using regex
    #         json_pattern = r'(\{(?:[^{}]|(?:\{[^{}]*\}))*\})'
    #         match = re.search(json_pattern, cleaned, re.DOTALL)
            
    #         if match:
    #             json_str = match.group(1)
    #             print(f"📝 Extracted JSON with regex: {json_str[:200]}...")
                
    #             try:
    #                 data = json.loads(json_str)
    #                 if isinstance(data, dict) and "recommendations" in data:
    #                     recommendations = data["recommendations"]
    #                     if isinstance(recommendations, list):
    #                         valid_recs = []
    #                         for rec in recommendations:
    #                             if isinstance(rec, dict) and "_id" in rec and "shops" in rec:
    #                                 valid_recs.append({
    #                                     "_id": str(rec["_id"]).strip(),
    #                                     "shops": str(rec["shops"]).strip()
    #                                 })
    #                         print(f"✅ Found {len(valid_recs)} valid recommendations via regex")
    #                         return valid_recs
    #             except json.JSONDecodeError:
    #                 pass
            
    #         # Step 4: Try to find individual _id and shops pairs
    #         # Pattern for: {"_id": "value", "shops": "value"}
    #         pair_pattern = r'\{\s*"_id"\s*:\s*"([^"]+)"\s*,\s*"shops"\s*:\s*"([^"]+)"\s*\}'
    #         pairs = re.findall(pair_pattern, cleaned)
            
    #         if pairs:
    #             recommendations = []
    #             for _id, shops in pairs:
    #                 recommendations.append({
    #                     "_id": _id.strip(),
    #                     "shops": shops.strip()
    #                 })
    #             print(f"✅ Found {len(recommendations)} recommendations via pair matching")
    #             return recommendations
            
    #         # Step 5: Last resort - look for any 24-char hex strings (MongoDB ObjectId) near shop names
    #         id_pattern = r'([a-f0-9]{24})'
    #         shop_pattern = r'"shops"\s*:\s*"([^"]+)"'
            
    #         ids = re.findall(id_pattern, cleaned)
    #         shops = re.findall(shop_pattern, cleaned)
            
    #         if ids and shops and len(ids) == len(shops):
    #             recommendations = []
    #             for i in range(min(len(ids), len(shops))):
    #                 recommendations.append({
    #                     "_id": ids[i].strip(),
    #                     "shops": shops[i].strip()
    #                 })
    #             print(f"✅ Found {len(recommendations)} recommendations via ID/shop matching")
    #             return recommendations
            
    #         print("⚠️ No valid recommendations found in output")
    #         return []
            
    #     except Exception as e:
    #         print(f"❌ Error parsing crew output: {type(e).__name__}: {str(e)}")
    #         import traceback
    #         traceback.print_exc()
    #         return []
    
    @staticmethod
    def parse_food_recommendations(output: str) -> List[Dict[str, str]]:
        """
        Parse crew output to extract food recommendation IDs and names.
        """
        try:
            print(f"🔍 Raw food output to parse (first 300 chars): {output[:300]}...")
            
            # Clean the output string first
            cleaned_output = output.strip()
            
            # Approach 1: Try to find and parse JSON array or object with recommendations
            json_match = re.search(r'\{[^{}]*"recommendations"[^{}]*\[[^\]]*\][^{}]*\}', cleaned_output, re.DOTALL)
            
            if json_match:
                try:
                    json_str = json_match.group(0)
                    # Remove all newlines and extra whitespace
                    json_str = ' '.join(json_str.split())
                    print(f"📝 Attempting to parse JSON: {json_str[:200]}...")
                    
                    data = json.loads(json_str)
                    if "recommendations" in data and isinstance(data["recommendations"], list):
                        valid_recs = []
                        for rec in data["recommendations"]:
                            # For food, we look for "name" or "foodPlace" field
                            if isinstance(rec, dict) and "_id" in rec:
                                name = rec.get("name") or rec.get("foodPlace") or "Unknown"
                                valid_recs.append({
                                    "_id": str(rec["_id"]).strip(),
                                    "name": str(name).strip()
                                })
                        
                        if valid_recs:
                            print(f"✅ Successfully parsed {len(valid_recs)} food recommendations via JSON")
                            return valid_recs
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"⚠️ JSON parsing failed: {e}")
            
            # Approach 2: Look for individual _id and name/foodPlace pairs using regex
            pattern = r'"_id"\s*:\s*"([^"]+)"\s*,\s*"(?:name|foodPlace)"\s*:\s*"([^"]+)"'
            matches = re.findall(pattern, cleaned_output, re.IGNORECASE)
            
            if matches:
                recommendations = []
                for _id, name in matches:
                    recommendations.append({
                        "_id": _id.strip(),
                        "name": name.strip()
                    })
                print(f"✅ Parsed {len(recommendations)} food recommendations via regex pattern matching")
                return recommendations
            
            # Approach 3: Try a more lenient pattern
            pattern2 = r'_id["\']?\s*:\s*["\']?([a-f0-9]{24})["\']?\s*,?\s*(?:name|foodPlace)["\']?\s*:\s*["\']?([^,\n\r}]+)'
            matches2 = re.findall(pattern2, cleaned_output, re.IGNORECASE)
            
            if matches2:
                recommendations = []
                for _id, name in matches2:
                    recommendations.append({
                        "_id": _id.strip().strip('"').strip("'"),
                        "name": name.strip().strip('"').strip("'")
                    })
                print(f"✅ Parsed {len(recommendations)} food recommendations via lenient regex")
                return recommendations
            
            # If we got here, no recommendations found
            print("⚠️ No valid food recommendations found in output")
            print(f"📄 Full output for debugging:\n{cleaned_output}")
            return []
            
        except Exception as e:
            print(f"❌ Error parsing crew output: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []