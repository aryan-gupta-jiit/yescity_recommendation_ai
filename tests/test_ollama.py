# test_ollama.py
import requests

try:
    response = requests.get("http://localhost:11434/api/tags")
    print(f"Ollama API Status: {response.status_code}")
    print(f"Available models: {response.json()}")
except Exception as e:
    print(f"Error connecting to Ollama: {e}")