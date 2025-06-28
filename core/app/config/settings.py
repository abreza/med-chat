import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-nano")
    APP_NAME = os.getenv("APP_NAME", "Medical AI Assistant")
    APP_URL = os.getenv("APP_URL", "https://localhost:7860")
    
    TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://tts-service:8001")
    
    DATA_DIR = Path.cwd() / "data"
