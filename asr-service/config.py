import os
from pathlib import Path


ASR_CONFIG = {
    "model_dir": Path(os.getenv("ASR_MODEL_DIR", "./data/dolphin/models")),
    "assets_dir": Path(os.getenv("ASR_ASSETS_DIR", "./data/dolphin/assets")),
    "default_model": os.getenv("ASR_DEFAULT_MODEL", "small"),
    "max_audio_duration": int(os.getenv("ASR_MAX_AUDIO_DURATION", "300")),
    "supported_formats": ["wav", "mp3", "m4a", "ogg", "flac"]
}


ASR_MODELS = {
    "base": {
        "name": "base (140M)",
        "size": "140M parameters",
        "url": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/base.pt"
    },
    "small": {
        "name": "small (372M)",
        "size": "372M parameters",
        "url": "https://huggingface.co/DataoceanAI/dolphin-small/resolve/main/small.pt"
    }
}


ASR_ASSET_URLS = {
    "bpe.model": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/bpe.model",
    "config.yaml": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/config.yaml",
    "feats_stats.npz": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/feats_stats.npz"
}


FASTAPI_CONFIG = {
    "title": "🎙️ ASR Microservice API",
    "version": "1.0.0",
    "contact": {
        "name": "ASR Service Support",
        "email": "support@example.com",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "servers": [
        {
            "url": "http://localhost:8002",
            "description": "Development server"
        }
    ]
}


TAGS_METADATA = [
    {
        "name": "Languages",
        "description": "Language and region management",
    },
    {
        "name": "Models",
        "description": "ASR model management",
    },
    {
        "name": "Transcription",
        "description": "Audio transcription endpoints",
    },
    {
        "name": "Health & Management",
        "description": "Health checks and cache management",
    },
]


SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": int(os.getenv("ASR_PORT", 8002)),
    "reload": os.getenv("ASR_RELOAD", "false").lower() == "true"
}
