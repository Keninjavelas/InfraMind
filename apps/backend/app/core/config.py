import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file, walking up the tree to find the root .env
load_dotenv(find_dotenv())

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
