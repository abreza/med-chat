import json
from typing import Dict, Any, List, Tuple, Optional
from .tts_config import TTSConfig
from ....utils.data import group_voices_by_language, sort_voices_by_quality


class VoiceManager:
    def __init__(self, config: TTSConfig):
        self.config = config
        self.voices = self._load_voices()
        self.current_settings = {
            "voice": self._get_default_voice(),
            "speaker": 0,
            "speed": 1.0,
            "noise_scale": 0.667,
            "noise_scale_w": 0.8,
        }

    def _load_voices(self) -> Dict[str, Any]:
        voices_file = self.config.data_dir / "piper" / "voices.json"
        if not voices_file.exists():
            return {}
        try:
            with open(voices_file, 'r', encoding='utf-8') as f:
                voices_data = json.load(f)
            processed_voices = {}
            for voice_key, voice_info in voices_data.items():
                onnx_file = config_file = None
                for file_path in voice_info.get("files", {}):
                    if file_path.endswith(".onnx"):
                        onnx_file = file_path
                    elif file_path.endswith(".onnx.json"):
                        config_file = file_path
                if onnx_file and config_file:
                    processed_voices[voice_key] = self._process_voice_info(
                        voice_key, voice_info, onnx_file, config_file)
            return processed_voices
        except Exception:
            return {}

    def _process_voice_info(self, voice_key: str, voice_info: Dict[str, Any], onnx_file: str, config_file: str) -> Dict[str, Any]:
        language_info = voice_info.get("language", {})
        voice_name = voice_info.get("name", voice_key)
        quality = voice_info.get("quality", "unknown")
        language_name = language_info.get("name_english", "Unknown")
        country = language_info.get("country_english", "")

        if country:
            display_name = f"{language_name} ({country}) - {voice_name} ({quality})"
        else:
            display_name = f"{language_name} - {voice_name} ({quality})"

        return {
            "name": display_name,
            "voice_name": voice_name,
            "language": voice_info.get("language", {}),
            "quality": quality,
            "num_speakers": voice_info.get("num_speakers", 1),
            "speaker_id_map": voice_info.get("speaker_id_map", {}),
            "model_url": self.config.base_url + onnx_file,
            "config_url": self.config.base_url + config_file,
            "model_file": onnx_file,
            "config_file": config_file,
            "files": voice_info.get("files", {})
        }

    def get_voice_options(self) -> List[Tuple[str, str]]:
        options = []
        language_groups = group_voices_by_language(self.voices)
        for lang_family in sorted(language_groups.keys()):
            sorted_voices = sort_voices_by_quality(
                language_groups[lang_family])
            options.extend(sorted_voices)
        return options

    def get_available_languages(self) -> List[str]:
        languages = set()
        for voice_info in self.voices.values():
            lang_family = voice_info["language"].get("family")
            if lang_family:
                languages.add(lang_family)
        return sorted(list(languages))

    def filter_voices_by_language(self, language_family: str) -> List[Tuple[str, str]]:
        filtered = []
        for voice_key, voice_info in self.voices.items():
            if voice_info["language"].get("family") == language_family:
                filtered.append((voice_info["name"], voice_key))
        return sort_voices_by_quality(filtered)

    def _get_default_voice(self) -> Optional[str]:
        if not self.voices:
            return None
        for voice_key, voice_info in self.voices.items():
            if voice_info["language"].get("family") == "fa":
                return voice_key
        for voice_key, voice_info in self.voices.items():
            if voice_info["language"].get("family") == "en":
                return voice_key
        return list(self.voices.keys())[0] if self.voices else None

    def get_voice_info(self, voice_key: str) -> Dict[str, Any]:
        return self.voices.get(voice_key, {})

    def get_speaker_count(self, voice_key: str) -> int:
        return self.voices.get(voice_key, {}).get("num_speakers", 1)

    def get_speaker_names(self, voice_key: str) -> List[str]:
        speaker_map = self.voices.get(voice_key, {}).get("speaker_id_map", {})
        return list(speaker_map.keys()) if speaker_map else []

    def update_settings(self, **kwargs) -> Dict[str, Any]:
        for key, value in kwargs.items():
            if key in self.current_settings and value is not None:
                if key == "voice" and value in self.voices:
                    self.current_settings[key] = value
                elif key == "speaker":
                    max_speakers = self.get_speaker_count(
                        self.current_settings["voice"])
                    self.current_settings[key] = max(
                        0, min(int(value), max_speakers - 1))
                elif key == "speed":
                    self.current_settings[key] = max(
                        0.1, min(3.0, float(value)))
                elif key in ["noise_scale", "noise_scale_w"]:
                    self.current_settings[key] = max(
                        0.0, min(1.0, float(value)))
        return self.current_settings.copy()

    def get_current_settings(self) -> Dict[str, Any]:
        return self.current_settings.copy()

    def validate_voice(self, voice_key: str) -> bool:
        return voice_key in self.voices
