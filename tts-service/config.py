import os
from pathlib import Path


TTS_CONFIG = {
    "model_dir": Path(os.getenv("TTS_MODEL_DIR", "./data/piper/models")),
    "voices_file": Path(os.getenv("TTS_VOICES_FILE", "./data/piper/voices.json")),
    "use_cuda": os.getenv("USE_CUDA", "false").lower() == "true",
    "ezafe_model_path": os.getenv("EZAFE_MODEL_PATH")
}


FASTAPI_CONFIG = {
    "title": "🎙️ TTS Microservice API",
    "version": "1.0.0",
    "contact": {
        "name": "TTS Service Support",
        "email": "support@example.com",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "servers": [
        {
            "url": "http://localhost:8001",
            "description": "Development server"
        }
    ]
}


TAGS_METADATA = [
    {
        "name": "Voices",
        "description": "Voice management and information",
    },
    {
        "name": "Speech Synthesis",
        "description": "Text-to-speech conversion endpoints",
    },
    {
        "name": "Health & Management",
        "description": "Health checks and cache management",
    },
]

SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": int(os.getenv("TTS_PORT", 8001)),
    "reload": os.getenv("TTS_RELOAD", "false").lower() == "true"
}
