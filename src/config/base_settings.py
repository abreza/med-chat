import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-nano")

APP_NAME = os.getenv("APP_NAME", "Voice AI Assistant")
APP_URL = os.getenv("APP_URL", "https://localhost:7860")

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

ASR_MODEL_DIR = os.path.join(DATA_DIR, "dolphin/models")
os.makedirs(ASR_MODEL_DIR, exist_ok=True)

PIPER_MODEL_DIR = os.path.join(DATA_DIR, "piper/models")
os.makedirs(PIPER_MODEL_DIR, exist_ok=True)

DOLPHIN_ASSETS_DIR = os.path.join(DATA_DIR, "dolphin/assets")
os.makedirs(DOLPHIN_ASSETS_DIR, exist_ok=True)