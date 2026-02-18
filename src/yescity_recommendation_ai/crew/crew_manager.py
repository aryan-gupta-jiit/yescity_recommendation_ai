from typing import Dict, List, Any, Optional
import os
from crewai import Agent, Task, Crew, Process,LLM
from langchain_community.llms import Ollama
from ..services.query_classifier import query_classifier, QueryCategory
from .yaml_loader import YAMLLoader
from ..tools.food_tools import food_search_tool
from ..tools.shopping_tools import shopping_search_tool
from .crew_output_parser import CrewOutputParser


class CrewManager:
    """Manages crew creation and execution based on query type."""
    
    def __init__(self):
        self.yaml_loader = YAMLLoader()
        self.available_agents = self.yaml_loader.get_available_agents()
        self.available_tasks = self.yaml_loader.get_available_tasks()
        
        # # Initialize Ollama LLM for CrewAI agents
        # ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        # ollama_model = os.getenv("OLLAMA_MODEL", "ollama/llama3.2:3b")
        # self.llm = Ollama(
        #     base_url=ollama_url,
        #     model=ollama_model,
        #     temperature=0.7,
        # )
        # Initialize Ollama LLM using CrewAI's LLM class
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "ollama/llama3.2:3b")
        print(ollama_model)
        # Method 1: Using CrewAI's LLM class with explicit Ollama provider
        self.llm = LLM(
            model=ollama_model,
            provider="ollama",  # Explicitly specify provider
            base_url=ollama_url,
            temperature=0.7,
            max_tokens=2000,
            timeout=60000,
        )
    
    def create_food_crew(self, city: str, query_details: str) -> Crew:
        """Create a crew for food recommendations."""
        
        # Load agent configuration
        agent_config = self.yaml_loader.load_agent_config("food_critic")
        
        # Create agent
        agent = Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", True),
            allow_delegation=agent_config.get("allow_delegation", False),
            tools=[food_search_tool],
            llm=self.llm  # Explicitly use Ollama LLM
        )
        
        # Load task configuration
        task_config = self.yaml_loader.load_task_config("food_recommendation")
        
        # Create task with dynamic parameters
        description = task_config["description"].format(
            cityName=city,
            user_query_details=query_details
        )
        
        task = Task(
            description=description,
            expected_output=task_config["expected_output"],
            agent=agent,
            async_execution=task_config.get("async_execution", False),
            output_file=task_config.get("output_file")
        )
        
        # Create crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            manager_llm=self.llm  # Explicitly use Ollama for crew manager
        )
        
        return crew
    
    # def create_shopping_crew(self, city: str, query_details: str) -> Crew:
    #     """Create a crew for shopping recommendations."""
        
    #     # Load agent configuration
    #     agent_config = self.yaml_loader.load_agent_config("shopping_guide")
        
    #     # Create agent
    #     agent = Agent(
    #         role=agent_config["role"],
    #         goal=agent_config["goal"],
    #         backstory=agent_config["backstory"],
    #         verbose=agent_config.get("verbose", True),
    #         allow_delegation=agent_config.get("allow_delegation", False),
    #         tools=[shopping_search_tool],
    #         llm=self.llm  # Explicitly use Ollama LLM
    #     )
        
    #     # Load task configuration
    #     task_config = self.yaml_loader.load_task_config("shopping_recommendation")
        
    #     # Create task with dynamic parameters
    #     description = task_config["description"].format(
    #         cityName=city,
    #         user_query_details=query_details
    #     )
        
    #     task = Task(
    #         description=description,
    #         expected_output=task_config["expected_output"],
    #         agent=agent,
    #         async_execution=task_config.get("async_execution", False),
    #         output_file=task_config.get("output_file")
    #     )
        
    #     # Create crew
    #     crew = Crew(
    #         agents=[agent],
    #         tasks=[task],
    #         process=Process.sequential,
    #         verbose=True,
    #         manager_llm=self.llm  # Explicitly use Ollama for crew manager
    #     )
        
    #     return crew

    # def create_shopping_crew(self, city: str, query_details: str, parameters: Dict = None) -> Crew:
    #     """Create a crew for shopping recommendations."""
        
    #     # Load agent configuration
    #     agent_config = self.yaml_loader.load_agent_config("shopping_guide")
        
    #     # Enhance agent with specific instructions
    #     backstory = agent_config["backstory"]
    #     if parameters and parameters.get("item_type"):
    #         backstory += f"\n\nThe user is specifically looking for: {parameters['item_type']}. Focus on finding shops that sell this item by analyzing their famousFor descriptions."
        
    #     # Create agent
    #     agent = Agent(
    #         role=agent_config["role"],
    #         goal=agent_config["goal"],
    #         backstory=backstory,
    #         verbose=agent_config.get("verbose", True),
    #         allow_delegation=agent_config.get("allow_delegation", False),
    #         tools=[shopping_search_tool],
    #         llm=self.llm
    #     )
        
    #     # Load task configuration
    #     task_config = self.yaml_loader.load_task_config("shopping_recommendation")
        
    #     # Create description with clear instructions
    #     params_str = ""
    #     if parameters:
    #         params_str = f"\n\nSPECIFIC USER REQUEST: Looking for {parameters.get('item_type', 'items')}"
    #         if parameters.get('preferences'):
    #             params_str += f" with preferences: {parameters['preferences']}"
        
    #     description = task_config["description"].format(
    #         cityName=city,
    #         user_query_details=query_details + params_str
    #     )
        
    #     # Add explicit instruction about analyzing all data
    #     description += "\n\nREMEMBER: The tool will return ALL shops in the city. You must analyze each shop's 'famousFor' field and name to find the most relevant matches for what the user wants."
        
    #     task = Task(
    #         description=description,
    #         expected_output=task_config["expected_output"],
    #         agent=agent,
    #         async_execution=task_config.get("async_execution", False)
    #     )
        
    #     # Create crew
    #     crew = Crew(
    #         agents=[agent],
    #         tasks=[task],
    #         process=Process.sequential,
    #         verbose=True
    #     )
        
    #     return crew

    # def create_shopping_crew(self, city: str, query_details: str, parameters: Dict = None) -> Crew:
    #     """Create a crew for shopping recommendations."""
        
    #     # Load agent configuration
    #     agent_config = self.yaml_loader.load_agent_config("shopping_guide")
        
    #     # Enhance agent with specific instructions
    #     backstory = agent_config["backstory"]
    #     if parameters and parameters.get("item_type"):
    #         backstory += f"\n\nThe user is specifically looking for: {parameters['item_type']}. Focus on finding shops that sell this item by analyzing their famousFor descriptions."
        
    #     # Create agent
    #     agent = Agent(
    #         role=agent_config["role"],
    #         goal=agent_config["goal"],
    #         backstory=backstory,
    #         verbose=agent_config.get("verbose", True),
    #         allow_delegation=agent_config.get("allow_delegation", False),
    #         tools=[shopping_search_tool],
    #         llm=self.llm,
    #         # Important: Add this to prevent tool argument errors
    #         max_iter=5,
    #         max_rpm=10
    #     )
        
    #     # Load task configuration
    #     task_config = self.yaml_loader.load_task_config("shopping_recommendation")
        
    #     # Create description with clear instructions
    #     params_str = ""
    #     if parameters:
    #         params_str = f"\n\nSPECIFIC USER REQUEST: Looking for {parameters.get('item_type', 'items')}"
    #         if parameters.get('preferences'):
    #             params_str += f" with preferences: {parameters['preferences']}"
        
    #     description = task_config["description"].format(
    #         cityName=city,
    #         user_query_details=query_details + params_str
    #     )
        
    #     # Add explicit instruction about what parameters to use
    #     description += """
        
    #     IMPORTANT: When using the search_shopping_places tool:
    #     - ONLY pass the cityName parameter (required)
    #     - DO NOT pass category or flagship parameters unless you're sure they're needed
    #     - Let the tool return ALL shops, then you analyze them
    #     - The tool will handle null values automatically
        
    #     Example correct tool usage:
    #     search_shopping_places(cityName="Agra")
        
    #     NOT:
    #     search_shopping_places(cityName="Agra", flagship='null', category='null')
    #     """
        
    #     task = Task(
    #         description=description,
    #         expected_output=task_config["expected_output"],
    #         agent=agent,
    #         async_execution=task_config.get("async_execution", False)
    #     )
        
    #     # Create crew
    #     crew = Crew(
    #         agents=[agent],
    #         tasks=[task],
    #         process=Process.sequential,
    #         verbose=True
    #     )
        
    #     return crew
    def create_shopping_crew(self, city: str, query_details: str, parameters: Dict = None) -> Crew:
        """Create a crew for shopping recommendations."""
        
        print("="*50)
        print("DEBUG: Inside create_shopping_crew")
        print(f"City: {city}")
        print(f"Query details: {query_details}")
        print(f"Parameters: {parameters}")
        
        try:
            print("DEBUG: Loading agent config...")
            agent_config = self.yaml_loader.load_agent_config("shopping_guide")
            print(f"DEBUG: Agent config loaded: {list(agent_config.keys())}")
            
            # Enhance agent with specific instructions
            backstory = agent_config["backstory"]
            print(f"DEBUG: Original backstory length: {len(backstory)}")
            
            if parameters and parameters.get("item_type"):
                backstory += f"\n\nThe user is specifically looking for: {parameters['item_type']}. Focus on finding shops that sell this item by analyzing their famousFor descriptions."
                print(f"DEBUG: Enhanced backstory with item_type: {parameters['item_type']}")
            
            print("DEBUG: Creating agent...")
            agent = Agent(
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=backstory,
                verbose=agent_config.get("verbose", True),
                allow_delegation=agent_config.get("allow_delegation", False),
                tools=[shopping_search_tool],
                llm=self.llm,
                max_iter=5,
                max_rpm=10,
                memory=False,
                function_calling_llm=self.llm
            )
            print(f"DEBUG: Agent created: {agent}")
            
            print("DEBUG: Loading task config...")
            task_config = self.yaml_loader.load_task_config("shopping_recommendation")
            print(f"DEBUG: Task config loaded: {list(task_config.keys())}")
            
            # Create description with clear instructions
            params_str = ""
            if parameters:
                params_str = f"\n\nSPECIFIC USER REQUEST: Looking for {parameters.get('item_type', parameters.get('product_type', 'items'))}"
                if parameters.get('preferences'):
                    params_str += f" with preferences: {parameters['preferences']}"
            
            print(f"DEBUG: Params string: {params_str}")
            
            description = task_config["description"].format(
                cityName=city,
                user_query_details=query_details + params_str
            )
            print(f"DEBUG: Description created, length: {len(description)}")
            
            # Add explicit instruction about what parameters to use
            description += """
            
            IMPORTANT: When using the search_shopping_places tool:
            - ONLY pass the cityName parameter (required)
            - DO NOT pass category or flagship parameters unless you're sure they're needed
            - Let the tool return ALL shops, then you analyze them
            - The tool will handle null values automatically
            
            Example correct tool usage:
            search_shopping_places(cityName="Agra")
            
            NOT:
            search_shopping_places(cityName="Agra", flagship='null', category='null')
            """
            
            print("DEBUG: Creating task...")
            task = Task(
                description=description,
                expected_output=task_config["expected_output"],
                agent=agent,
                async_execution=task_config.get("async_execution", False)
            )
            print(f"DEBUG: Task created: {task}")
            
            print("DEBUG: Creating crew...")
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            print(f"DEBUG: Crew created: {crew}")
            print("DEBUG: Returning crew")
            print("="*50)
            
            return crew
            
        except Exception as e:
            print("="*50)
            print("❌ EXCEPTION IN create_shopping_crew")
            print(f"Exception type: {type(e)}")
            print(f"Exception message: {str(e)}")
            print(f"Exception repr: {repr(e)}")
            import traceback
            traceback.print_exc()
            print("="*50)
            raise  # Re-raise the exception so we can see it in the caller
        
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query and return recommendations.
        
        Args:
            user_query: The natural language query from user
            
        Returns:
            Dictionary with recommendations and metadata
        """
        # Step 1: Classify the query
        classification = query_classifier.classify_query(user_query)
        
        # Step 2: Create appropriate crew based on category
        if classification.category == "foods":
            if not classification.cityName:
                return {
                    "success": False,
                    "error": "Please specify a city for food recommendations.",
                    "category": "foods"
                }
            
            # Extract parameters for food search
            params = classification.parameters
            query_details = f"Looking for food in {classification.cityName}"
            if params:
                query_details += f" with parameters: {params}"
            
            # Create and execute food crew
            crew = self.create_food_crew(classification.cityName, query_details)
            
            try:
                result = crew.kickoff()
                print(f"Crew Output: {result}")
                
                # Parse the output to get recommendations
                recommendations = CrewOutputParser.parse_food_recommendations(str(result))
                
                return {
                    "success": True,
                    "category": "foods",
                    "city": classification.cityName,
                    "parameters": params,
                    "recommendations": recommendations,
                    "raw_output": str(result)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error executing crew: {str(e)}",
                    "category": "foods"
                }
        
        elif classification.category in ["shoppings", "shopping"]:
            if not classification.cityName:
                return {
                    "success": False,
                    "error": "Please specify a city for shopping recommendations.",
                    "category": "shoppings"
                }
            
            # Extract parameters for shopping search
            params = classification.parameters
            query_details = f"Looking for shopping in {classification.cityName}"
            if params:
                query_details += f" with parameters: {params}"
            print("="*50)
            print("STEP 1: Creating shopping crew")
            print(f"City: {classification.cityName}")
            print(f"Params: {params}")
            print(f"Query details: {query_details}")
            # Create and execute shopping crew
            crew = self.create_shopping_crew(classification.cityName, query_details)
            print("STEP 2: Crew created successfully")
            print(f"Crew type: {type(crew)}")
            
            print("STEP 3: About to call crew.kickoff()...")
            try:
                print("🔄 About to call crew.kickoff()...")
                print("STEP 4: crew.kickoff() completed successfully")
                result = crew.kickoff()
                print(f"Crew Output: {result}")
                print(f"Crew Output Type: {type(result)}")
                print(f"Crew Output String Representation (first 1000 chars): {str(result)[:1000]}")
                
                # Parse the output to get recommendations
                recommendations = CrewOutputParser.parse_shopping_recommendations(str(result))
                
                print(f"Parsed recommendations: {recommendations}")
                print(f"Number of recommendations: {len(recommendations)}")
                
                if not recommendations:
                    print("⚠️ WARNING: Parser returned empty recommendations list!")
                
                return {
                    "success": True,
                    "category": "shoppings",
                    "city": classification.cityName,
                    "parameters": params,
                    "recommendations": recommendations,
                    "raw_output": str(result)
                }
                
            # except Exception as e:
            #     return {
            #         "success": False,
            #         "error": f"Error executing crew: {str(e)}",
            #         "category": "shoppings"
            #     }
            except Exception as e:
                        print("="*50)
                        print("EXCEPTION CAUGHT IN CREW MANAGER")
                        print(f"Exception type: {type(e)}")
                        print(f"Exception message: {str(e)}")
                        print(f"Exception repr: {repr(e)}")
                        import traceback
                        traceback.print_exc()
                        print("="*50)
                        
                        return {
                            "success": False,
                            "error": f"Error executing crew: {str(e)}",
                            "category": "shoppings"
                        }
        
        else:
            # For now, return placeholder for other categories
            return {
                "success": False,
                "error": f"Category '{classification.category}' not implemented yet.",
                "category": classification.category,
                "city": classification.cityName
            }

# Create singleton instance
crew_manager = CrewManager()