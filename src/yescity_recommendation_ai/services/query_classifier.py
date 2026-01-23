import os
import json
from typing import Dict, Optional
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class QueryCategory(BaseModel):
    """ Represents the classified query category. """
    category: str # e.g. "foods", "atcomodations", "activities", etc.
    cityName: Optional[str] = None
    parameters: Dict[str, str] = {}
    confidence: float = 0.0

class OllamaQueryClassifier:
    """ Classifies user queries using Ollama Local LLM. """

    def __init__(self):
        Ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b")

        self.llm = Ollama(
            base_url=Ollama_url,
            model=ollama_model,
            temperature=0.1,
        )

        # Define available categories based on your collections

        self.categories = [
            "foods",
            "accommodations",
            "activities",
            "cityinfos",
            "localtransports",
            "hiddengems",
            "connectivities",
            "placestovisits",
            "shopping"
        ]

        # Create prompt template

        self.prompt_template = PromptTemplate(

            input_variables=["query", "categories"],
            template="""
                You are a travel query classifier for YesCity travel assistant.

                COLLECTIONS in database:
                1. foods - restaurants, cafes, street food, local delicacies
                2. accommodations - rooms, hotels, hostels, guesthouses, vacation rentals, stays
                3. activities - things to do, experinces
                4. cityinfos - general city information
                5. localtransports - local transportation, public transport, taxis, bike rentals
                6. connectivites - internet, SIM cards, WiFi spots
                7. hiddengems - lesser known local spots, off-the-beaten-path places, unique spots
                8. placestovisits - popular tourist attractions, landmarks, must-see places
                9. shopping - markets, malls, shopping streets, local products, shops, souvenirs

                classify this user query into ONE category from: {categories}

                Also extract:
                1. The city name ( extracted from query if mentioned)
                2. key parameters relevant to the category

                User Query: "{query}"

                Respond ONLY with valid JSON in this exact format:
                {{
                    "category":"category_name",
                    "cityName":"city_name_or_null",
                    "parameters":
                    {{
                        "param1":"value1",
                        "param2":"value2"
                    }},
                    "confidence":confidence_score_between_0_and_1
                }}

                Example response for "Find pizza places in Agra":
                {{
                    "category":"foods",
                    "cityName":"Agra",
                    "parameters":
                    {{
                        "category": "pizza",
                        "food_type": "restaurant"
                    }},
                    "confidence":0.95
                }}

                IMPORTANT: If city is not mentioned, use "cityName": null
            """
        )

    def classify_query(self, user_query: str) -> QueryCategory:

            try:
                prompt=self.prompt_template.format(
                    query=user_query,
                    categories=", ".join(self.categories)
                )

                response=self.llm.invoke(prompt)

                print(f"Ollama response: {response}")

                # Try to parse JSON from response
                # Find JSON object in response
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1

                if start_idx != -1 or end_idx != -1:
                    json_str=response[start_idx:end_idx]
                    data=json.loads(json_str)

                    # Validate category
                    category=data.get("category","cityinfos")
                    if category not in self.categories:
                        category="cityinfos"

                    return QueryCategory(
                        category=category,
                        cityName=data.get("cityName"),
                        parameters=data.get("parameters",{}),
                        confidence=data.get("confidence",0.5)
                    )
                else:
                    return self._fallback_classification(user_query)
            
            except Exception as e:
                print(f"❌ Error classifying query with Ollama: {e}")
                return self._fallback_classification(user_query)
            
    def _fallback_classification(self, user_query: str) -> QueryCategory:
        """Fallback classification using keyword matching."""
        query_lower = user_query.lower()
        
        # Keyword mapping
        keyword_mapping = {
            "food": "foods",
            "restaurant": "foods",
            "eat": "foods",
            "dinner": "foods",
            "lunch": "foods",
            "breakfast": "foods",
            "cafe": "foods",
            "sweet": "foods",
            "petha": "foods",
            "hotel": "accommodations",
            "stay": "accommodations",
            "accommodation": "accommodations",
            "activity": "activities",
            "do": "activities",
            "see": "places_to_visit",
            "visit": "places_to_visit",
            "attraction": "places_to_visit",
            "shop": "shopping",
            "buy": "shopping",
            "market": "shopping",
            "transport": "localtransports",
            "bus": "localtransports",
            "train": "localtransports",
            "hidden": "hiddengems",
            "gem": "hiddengems",
            "local": "hiddengems"
        }
        
        # Find city name (simplified)
        cities = ["Agra", "Delhi", "Mumbai", "Bangalore", "Jaipur", "Goa", "Chennai", "Kolkata"]
        found_city = None
        for city in cities:
            if city.lower() in query_lower:
                found_city = city
                break
        
        # Determine category
        category = "cityinfos"  # default
        for keyword, cat in keyword_mapping.items():
            if keyword in query_lower:
                category = cat
                break
        
        return QueryCategory(
            category=category,
            cityName=found_city,
            parameters={},
            confidence=0.5
        )

# Create singleton instance
query_classifier = OllamaQueryClassifier()
        