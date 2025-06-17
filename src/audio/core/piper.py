import os
import urllib.request
from typing import Optional, Dict, Any
from src.config.base_settings import PIPER_MODEL_DIR
from src.config.tts_settings import PIPER_VOICES

_model_cache: Dict[str, Any] = {}


def get_voice_file_paths(voice_key: str) -> tuple[Optional[str], Optional[str]]:
    if voice_key not in PIPER_VOICES:
        return None, None

    voice_info = PIPER_VOICES[voice_key]
    model_path = None
    config_path = None

    for file_path, file_info in voice_info.get("files", {}).items():
        if file_path.endswith(".onnx"):
            model_path = os.path.join(PIPER_MODEL_DIR, file_path)
        elif file_path.endswith(".onnx.json"):
            config_path = os.path.join(PIPER_MODEL_DIR, file_path)

    return model_path, config_path


def download_piper_voice(voice_key: str) -> bool:
    if voice_key not in PIPER_VOICES:
        print(f"Unknown voice: {voice_key}")
        return False

    voice_info = PIPER_VOICES[voice_key]
    model_path, config_path = get_voice_file_paths(voice_key)

    if not model_path or not config_path:
        print(f"Could not determine file paths for voice: {voice_key}")
        return False

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    if not os.path.exists(model_path):
        try:
            print(f"Downloading Piper voice model: {voice_key}")
            print(f"URL: {voice_info['model_url']}")
            urllib.request.urlretrieve(voice_info["model_url"], model_path)
            print(f"Downloaded {model_path}")
        except Exception as e:
            print(f"Error downloading model {voice_key}: {e}")
            return False

    if not os.path.exists(config_path):
        try:
            print(f"Downloading Piper voice config: {voice_key}")
            print(f"URL: {voice_info['config_url']}")
            urllib.request.urlretrieve(voice_info["config_url"], config_path)
            print(f"Downloaded {config_path}")
        except Exception as e:
            print(f"Error downloading config {voice_key}: {e}")
            return False

    return True


def load_model(voice_key: str) -> Optional[Any]:
    global _model_cache

    if voice_key in _model_cache:
        print(f"Using cached model for voice: {voice_key}")
        return _model_cache[voice_key]

    try:
        from piper.voice import PiperVoice

        model_path, config_path = get_voice_file_paths(voice_key)

        if not model_path:
            print(f"Could not determine model path for voice: {voice_key}")
            return None

        if not os.path.exists(model_path):
            print(f"Model file not found locally: {model_path}")
            if not download_piper_voice(voice_key):
                return None

        print(f"Loading Piper voice: {voice_key}")
        print(f"Model path: {model_path}")

        model = PiperVoice.load(model_path)

        _model_cache[voice_key] = model

        print(f"Successfully loaded and cached Piper voice: {voice_key}")
        return model

    except ImportError:
        print("Piper TTS not installed. Install with: pip install piper-tts")
        return None
    except Exception as e:
        print(f"Error loading Piper voice {voice_key}: {e}")
        return None
