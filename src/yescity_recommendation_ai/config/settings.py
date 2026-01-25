# import os
# from crewai import LLM
# from dotenv import load_dotenv

# load_dotenv()

# def get_llm_config():
#     """ Get Ollama LLM configuration"""

#     ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#     ollama_model=os.getenv("OLLAMA_MODEL", "yescity-recommendation-ai")

#     return LLM(
#         model=f"{ollama_url}/{ollama_model}",
#         temperature=0.3,
#         max_tokens=1000
#     )

# llm=get_llm_config()

import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

def get_llm_config():
    """Get Ollama LLM configuration with explicit provider"""
    
    ollama_model = os.getenv("OLLAMA_MODEL", "ollama/llama3.2:3b")
    
    # Explicitly configure Ollama provider
    return LLM(
        config={
            "provider": "ollama",  # Explicitly set provider to ollama
            "model": ollama_model,
            "temperature": 0.3,
            "max_tokens": 1000,
            "base_url": "http://localhost:11434",  # Optional, but good to specify
        }
    )

llm = get_llm_config()