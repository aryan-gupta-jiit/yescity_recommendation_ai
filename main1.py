
import os
import sys
import json
from typing import Dict, Any, List

# Add src to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Import capabilities
from src.yescity_recommendation_ai.services.query_classifier import query_classifier, QueryCategory
from src.yescity_recommendation_ai.tools.food_tools import food_search_tool
from src.yescity_recommendation_ai.tools.shopping_tools import shopping_search_tool
from src.yescity_recommendation_ai.database.mongodb_client import mongodb_client

load_dotenv()

def format_tool_results(results: List[Dict[str, Any]]) -> str:
    """Format tool results into a readable string for the LLM."""
    if not results:
        return "No results found."
    
    formatted = []
    # Limit context size by processing max 20 results if too many
    # Sorting by relevance or quality would be ideal here if possible
    processed_results = results[:20] if len(results) > 20 else results
    
    for i, item in enumerate(processed_results, 1):
        # Extract key fields for conciseness
        _id = item.get('_id', 'N/A')
        name = item.get('shops') or item.get('foodPlace') or "Unknown Place"
        address = item.get('address', 'No address')
        desc = item.get('famousFor') or item.get('description') or "No description"
        category = item.get('category', 'General')
        
        entry = f"{i}. ID: {_id} | Name: {name} | Category: {category} | Details: {desc}"
             
        formatted.append(entry)
    
    if len(results) > 20:
        formatted.append(f"... and {len(results) - 20} more results.")
        
    return "\n".join(formatted)

def main():
    print("🚀 YesCity Direct Assistant (No Agent Framework)")
    print("Type 'exit' or 'quit' to stop.")
    
    # Ensure MongoDB connection
    try:
        if mongodb_client.db is None:
            print("❌ Failed to connect to database.")
            return
    except Exception as e:
        print(f"❌ Database error: {e}")
        return

    # Initialize generation LLM once
    from langchain_community.llms import Ollama
    generation_llm = Ollama(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model="llama3.2:3b",
        temperature=0.1, # Lower temperature for valid JSON
        num_ctx=8192 # Request larger context window if supported
    )

    while True:
        try:
            user_query = input("\n👤 You: ")
            if user_query.lower() in ['exit', 'quit']:
                break
            
            if not user_query.strip():
                continue

            print("\n🤖 Classifying...")
            classification: QueryCategory = query_classifier.classify_query(user_query)
            
            print(f"   Category: {classification.category}")
            print(f"   City: {classification.cityName}")
            print(f"   Params: {classification.parameters}")
            
            tool_results = []
            
            # Direct Tool Calling
            if classification.category == "foods":
                print("   Invoking FoodSearchTool...")
                category_filter = classification.parameters.get("category") or classification.parameters.get("food_type")
                
                veg_only = False
                if "veg" in user_query.lower() and "non" not in user_query.lower():
                     veg_only = True
                
                results = food_search_tool._run(
                    cityName=classification.cityName,
                    category=category_filter,
                    vegOnly=veg_only,
                    maxResults=50 # Increased limit
                )
                tool_results = results

            elif classification.category == "shoppings":
                print("   Invoking ShoppingSearchTool...")
                category_filter = classification.parameters.get("category")
                
                # If specific shopping type is not found, try broader search first
                # For "rudraksha", category might be missing or misleading if not in DB taxonomy
                # So we prioritize city search if category causes empty results
                
                results = shopping_search_tool._run(
                    cityName=classification.cityName,
                    category=category_filter,
                    maxResults=50 # Increased limit
                )
                tool_results = results
                
            else:
                print(f"⚠️ Tool for category '{classification.category}' is not implemented in this script yet.")
                tool_results = []

            # Generate Answer using LLM
            print("   Generating response with llama3.2:3b...")
            
            results_text = format_tool_results(tool_results)
            
            # Construct prompt
            system_prompt = """You are a helpful travel assistant.
            
            IMPORTANT: You must response with a RAW JSON object ONLY. No markdown formatting, no code blocks, no explanation text.
            
            Goal: Recommend top 3 places from the provided database results based on the user's query.

            OUTPUT FORMAT:
            {
                "recommendations": [
                    {"_id": "unique_id_string", "shops": "Place Name"},
                    {"_id": "unique_id_string", "shops": "Place Name"}
                ]
            }

            RULES:
            1. Each recommendation must have "_id" (as string) and "shops" (or "foodPlace" mapped to "shops").
            2. Maximum 3 recommendations.
            3. If no matches found, return: {"recommendations": []}
            4. Do NOT include any other text, notes, or explanation.
            5. Extract the "_id" exactly as provided in the database results.
            """
            
            user_prompt = f"""
            User Query: "{user_query}"
            
            Database Results:
            {results_text}
            
            Generate JSON response:
            """
            
            response = generation_llm.invoke(f"{system_prompt}\n\n{user_prompt}")
            
            print(f"\n🤖 Agent: {response}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
