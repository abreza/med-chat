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
    TTS_MODEL_DIR = DATA_DIR / "piper" / "models"

    @classmethod
    def ensure_directories(cls):
        for directory in [cls.DATA_DIR, cls.TTS_MODEL_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


Config.ensure_directories()
