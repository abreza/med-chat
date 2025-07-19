import os
import urllib.request
import shutil
import tempfile
import base64
from typing import Optional, Dict, List, Any
import torch
import dolphin
from config import ASR_CONFIG, ASR_MODELS, ASR_ASSET_URLS


dolphin_model = None
current_model_key = "small"
model_cache = {}


def download_file(url: str, dest_path: str) -> bool:
    if os.path.exists(dest_path):
        return True

    try:
        print(f"Downloading {url} to {dest_path}")
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Downloaded {dest_path}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def ensure_assets_downloaded() -> bool:
    ASR_CONFIG["assets_dir"].mkdir(parents=True, exist_ok=True)

    for filename, url in ASR_ASSET_URLS.items():
        dest_path = ASR_CONFIG["assets_dir"] / filename
        if not download_file(url, str(dest_path)):
            return False
    return True


def ensure_model_downloaded(model_key: str) -> Optional[str]:
    if model_key not in ASR_MODELS:
        print(f"Unknown model: {model_key}")
        return None

    ASR_CONFIG["model_dir"].mkdir(parents=True, exist_ok=True)
    model_path = ASR_CONFIG["model_dir"] / f"{model_key}.pt"

    if download_file(ASR_MODELS[model_key]["url"], str(model_path)):
        return str(model_path)
    return None


def setup_dolphin_model(model_key: str = "small") -> bool:
    global dolphin_model, current_model_key, model_cache

    if model_key in model_cache:
        dolphin_model = model_cache[model_key]
        current_model_key = model_key
        return True

    try:
        print(f"Loading Dolphin ASR model: {model_key}")

        if not ensure_assets_downloaded():
            print("Failed to download required assets")
            return False

        model_path = ensure_model_downloaded(model_key)
        if not model_path:
            print(f"Failed to download model: {model_key}")
            return False

        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load model
        model = dolphin.load_model(
            model_key,
            str(ASR_CONFIG["model_dir"]),
            device,
            assets_dir=str(ASR_CONFIG["assets_dir"])
        )

        # Cache the model
        model_cache[model_key] = model
        dolphin_model = model
        current_model_key = model_key

        print(f"Dolphin ASR model loaded successfully on {device}")
        return True

    except Exception as e:
        print(f"Error loading Dolphin ASR model: {e}")
        return False


def convert_audio_to_wav_file(audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
    if not audio_data:
        return None

    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

        if isinstance(audio_data, bytes):
            # If it's raw bytes, try to interpret as audio
            temp_file.write(audio_data)
            temp_file.close()
            return temp_file.name
        else:
            temp_file.close()
            os.unlink(temp_file.name)
            return None

    except Exception as e:
        print(f"Error converting audio data: {e}")
        return None


def transcribe_audio_file(file_path: str, language: Optional[str] = None, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
    global dolphin_model

    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return None

    if dolphin_model is None:
        print("Dolphin ASR model is not loaded")
        return None

    try:
        # Load audio
        waveform = dolphin.load_audio(file_path)

        # Prepare transcription kwargs
        kwargs = {
            "predict_time": False,
            "padding_speech": False
        }

        if language:
            kwargs["lang_sym"] = language
        if region:
            kwargs["region_sym"] = region

        # Transcribe
        result = dolphin_model(waveform, **kwargs)

        transcription = result.text.strip() if hasattr(result, 'text') else ""
        detected_language = getattr(result, 'language', None)
        detected_region = getattr(result, 'region', None)
        confidence = getattr(result, 'confidence', None)

        return {
            'text': transcription,
            'language': detected_language,
            'region': detected_region,
            'confidence': confidence
        }

    except Exception as e:
        print(f"Transcription error for file {file_path}: {e}")
        return None


def transcribe_base64_audio(base64_audio: str, language: Optional[str] = None, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(base64_audio)

        # Convert to temporary WAV file
        temp_file_path = convert_audio_to_wav_file(audio_data)
        if not temp_file_path:
            print("Failed to convert audio data to WAV file")
            return None

        try:
            # Transcribe
            result = transcribe_audio_file(temp_file_path, language, region)
            return result

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        print(f"Error transcribing base64 audio: {e}")
        return None


def get_available_languages() -> List[Dict[str, Any]]:
    try:
        from dolphin.languages import LANGUAGE_CODES, LANGUAGE_REGION_CODES

        languages = []

        # Build language to regions mapping
        language_to_regions = {}
        for lang_region, names in LANGUAGE_REGION_CODES.items():
            if "-" in lang_region:
                lang, region = lang_region.split("-", 1)
                if lang not in language_to_regions:
                    language_to_regions[lang] = []
                language_to_regions[lang].append({
                    "code": region,
                    "name": names[0]
                })

        # Build language list
        for code, name in LANGUAGE_CODES.items():
            regions = language_to_regions.get(code, [])
            languages.append({
                "code": code,
                "name": name[0],
                "regions": regions
            })

        return sorted(languages, key=lambda x: x["name"])

    except ImportError:
        # Fallback if dolphin.languages is not available
        return [
            {"code": "en", "name": "English", "regions": [
                {"code": "US", "name": "United States"}]},
            {"code": "fa", "name": "Persian", "regions": [
                {"code": "IR", "name": "Iran"}]},
            {"code": "ar", "name": "Arabic", "regions": [
                {"code": "SA", "name": "Saudi Arabia"}]}
        ]


def get_available_models() -> Dict[str, Dict[str, str]]:
    return ASR_MODELS


def get_current_model() -> Optional[str]:
    return current_model_key if dolphin_model else None


def clear_model_cache() -> int:
    global model_cache, dolphin_model, current_model_key

    cached_count = len(model_cache)
    model_cache.clear()
    dolphin_model = None
    current_model_key = None

    return cached_count


def get_model_cache_size() -> int:
    return len(model_cache)
