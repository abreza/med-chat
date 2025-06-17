import json
import os
from src.config.base_settings import DATA_DIR

PIPER_VOICES_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"

VOICES_JSON_PATH = os.path.join(DATA_DIR, "piper", "voices.json")


def load_piper_voices():
    if not os.path.exists(VOICES_JSON_PATH):
        print(f"Warning: voices.json not found at {VOICES_JSON_PATH}")
        return {}

    try:
        with open(VOICES_JSON_PATH, 'r', encoding='utf-8') as f:
            voices_data = json.load(f)

        piper_voices = {}

        for voice_key, voice_info in voices_data.items():
            onnx_file = None
            config_file = None

            for file_path, file_info in voice_info.get("files", {}).items():
                if file_path.endswith(".onnx"):
                    onnx_file = file_path
                elif file_path.endswith(".onnx.json"):
                    config_file = file_path

            if onnx_file and config_file:
                language_info = voice_info.get("language", {})
                voice_name = voice_info.get("name", voice_key)
                quality = voice_info.get("quality", "unknown")

                language_name = language_info.get("name_english", "Unknown")
                country = language_info.get("country_english", "")
                if country:
                    display_name = f"{language_name} ({country}) - {voice_name} ({quality})"
                else:
                    display_name = f"{language_name} - {voice_name} ({quality})"

                piper_voices[voice_key] = {
                    "name": display_name,
                    "voice_name": voice_name,
                    "language": voice_info.get("language", {}),
                    "quality": quality,
                    "num_speakers": voice_info.get("num_speakers", 1),
                    "speaker_id_map": voice_info.get("speaker_id_map", {}),
                    "model_url": PIPER_VOICES_BASE_URL + onnx_file,
                    "config_url": PIPER_VOICES_BASE_URL + config_file,
                    "model_file": onnx_file,
                    "config_file": config_file,
                    "files": voice_info.get("files", {})
                }

        print(f"Loaded {len(piper_voices)} Piper voices from voices.json")
        return piper_voices

    except Exception as e:
        print(f"Error loading voices.json: {e}")
        return {}


PIPER_VOICES = load_piper_voices()


def create_piper_voice_options():
    options = []
    language_groups = {}

    for voice_key, voice_info in PIPER_VOICES.items():
        lang_family = voice_info["language"].get("family", "unknown")
        if lang_family not in language_groups:
            language_groups[lang_family] = []
        language_groups[lang_family].append((voice_info["name"], voice_key))

    for lang_family in sorted(language_groups.keys()):
        language_groups[lang_family].sort(key=lambda x: x[0])
        options.extend(language_groups[lang_family])

    return options


piper_voice_options = create_piper_voice_options()


def get_default_voice():
    for voice_key, voice_info in PIPER_VOICES.items():
        if voice_info["language"].get("family") == "fa":
            return voice_key

    for voice_key, voice_info in PIPER_VOICES.items():
        if voice_info["language"].get("family") == "en":
            return voice_key

    if PIPER_VOICES:
        return list(PIPER_VOICES.keys())[0]

    return None


current_piper_voice = get_default_voice()
current_piper_speaker = 0
current_piper_speed = 1.0
current_piper_noise_scale = 0.667
current_piper_noise_scale_w = 0.8


def get_voice_speaker_count(voice_key):
    if voice_key in PIPER_VOICES:
        return PIPER_VOICES[voice_key].get("num_speakers", 1)
    return 1


def get_voice_speaker_names(voice_key):
    if voice_key in PIPER_VOICES:
        speaker_map = PIPER_VOICES[voice_key].get("speaker_id_map", {})
        if speaker_map:
            return list(speaker_map.keys())
    return []


def filter_voices_by_language(language_family):
    filtered = []
    for voice_key, voice_info in PIPER_VOICES.items():
        if voice_info["language"].get("family") == language_family:
            filtered.append((voice_info["name"], voice_key))
    return sorted(filtered, key=lambda x: x[0])


def get_available_languages():
    languages = set()
    for voice_info in PIPER_VOICES.values():
        lang_family = voice_info["language"].get("family")
        if lang_family:
            languages.add(lang_family)
    return sorted(list(languages))
