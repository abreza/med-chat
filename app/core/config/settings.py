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
    
    BASE_DIR = Path.cwd()
    DATA_DIR = BASE_DIR / "data"
    
    ASR_MODEL_DIR = DATA_DIR / "dolphin" / "models"
    TTS_MODEL_DIR = DATA_DIR / "piper" / "models"
    DOLPHIN_ASSETS_DIR = DATA_DIR / "dolphin" / "assets"
    
    @classmethod
    def ensure_directories(cls):
        directories = [
            cls.DATA_DIR,
            cls.ASR_MODEL_DIR,
            cls.TTS_MODEL_DIR,
            cls.DOLPHIN_ASSETS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

Config.ensure_directories()
