import yaml
import os
from typing import Dict, Any
from pathlib import Path

class YAMLLoader:
    """Utility class to load YAML configuration files."""
    
    @staticmethod
    def load_agent_config(agent_name: str) -> Dict[str, Any]:
        """Load agent configuration from YAML file."""
        config_path = Path(__file__).parent.parent / "config" / "agents" / f"{agent_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        return config
    
    @staticmethod
    def load_task_config(task_name: str) -> Dict[str, Any]:
        """Load task configuration from YAML file."""
        config_path = Path(__file__).parent.parent / "config" / "tasks" / f"{task_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Task config not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        return config
    
    @staticmethod
    def get_available_agents() -> list:
        """Get list of available agent configurations."""
        agents_dir = Path(__file__).parent.parent / "config" / "agents"
        if not agents_dir.exists():
            return []
        
        agents = []
        for file in agents_dir.glob("*.yaml"):
            agents.append(file.stem)  # Get filename without extension
        
        return agents
    
    @staticmethod
    def get_available_tasks() -> list:
        """Get list of available task configurations."""
        tasks_dir = Path(__file__).parent.parent / "config" / "tasks"
        if not tasks_dir.exists():
            return []
        
        tasks = []
        for file in tasks_dir.glob("*.yaml"):
            tasks.append(file.stem)  # Get filename without extension
        
        return tasks