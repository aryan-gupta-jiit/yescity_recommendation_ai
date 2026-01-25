from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew, Process
from ..services.query_classifier import query_classifier, QueryCategory
from .yaml_loader import YAMLLoader
from ..tools.food_tools import food_search_tool
from .crew_output_parser import CrewOutputParser

class CrewManager:
    """Manages crew creation and execution based on query type."""
    
    def __init__(self):
        self.yaml_loader = YAMLLoader()
        self.available_agents = self.yaml_loader.get_available_agents()
        self.available_tasks = self.yaml_loader.get_available_tasks()
    
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
            tools=[food_search_tool]
        )
        
        # Load task configuration
        task_config = self.yaml_loader.load_task_config("food_recommendation")
        
        # Create task with dynamic parameters
        description = task_config["description"].format(
            city=city,
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
            verbose=True
        )
        
        return crew
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query and return recommendations.
        
        Args:
            user_query: The natural language query from user
            
        Returns:
            Dictionary with recommendations and metadata
        """
        # Step 1: Classify the query
        classification = query_classifier.classify(user_query)
        
        # Step 2: Create appropriate crew based on category
        if classification.category == "food":
            if not classification.city:
                return {
                    "success": False,
                    "error": "Please specify a city for food recommendations.",
                    "category": "food"
                }
            
            # Extract parameters for food search
            params = classification.parameters
            query_details = f"Looking for food in {classification.city}"
            if params:
                query_details += f" with parameters: {params}"
            
            # Create and execute food crew
            crew = self.create_food_crew(classification.city, query_details)
            
            try:
                result = crew.kickoff()
                print(f"Crew Output: {result}")
                
                # Parse the output to get recommendations
                recommendations = CrewOutputParser.parse_food_recommendations(str(result))
                
                return {
                    "success": True,
                    "category": "food",
                    "city": classification.city,
                    "parameters": params,
                    "recommendations": recommendations,
                    "raw_output": str(result)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error executing crew: {str(e)}",
                    "category": "food"
                }
        
        else:
            # For now, return placeholder for other categories
            return {
                "success": False,
                "error": f"Category '{classification.category}' not implemented yet.",
                "category": classification.category,
                "city": classification.city
            }

# Create singleton instance
crew_manager = CrewManager()