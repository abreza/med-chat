from typing import Optional, Dict, Any, List, Tuple
from app.clients.tts import TTSServiceClient


class TTSManager:
    def __init__(self, tts_client: TTSServiceClient = None):
        self.tts_client = tts_client or TTSServiceClient()
        self.current_settings = {
            "voice": self._get_default_voice(),
            "speaker": 0,
            "speed": 1.0,
            "noise_scale": 0.667,
            "noise_scale_w": 0.8,
        }

    def _get_default_voice(self) -> Optional[str]:
        voices = self.tts_client.get_voices()
        if not voices:
            return None

        for voice_key, voice_info in voices.items():
            lang_family = voice_info.get("language", {}).get("family")
            if lang_family == "fa":
                return voice_key

        for voice_key, voice_info in voices.items():
            lang_family = voice_info.get("language", {}).get("family")
            if lang_family == "en":
                return voice_key

        return list(voices.keys())[0] if voices else None

    def get_voice_options(self) -> List[Tuple[str, str]]:
        voices = self.tts_client.get_voices()
        if not voices:
            return []

        options = []
        language_groups = {}

        for voice_key, voice_info in voices.items():
            lang_family = voice_info.get(
                "language", {}).get("family", "unknown")
            if lang_family not in language_groups:
                language_groups[lang_family] = []
            language_groups[lang_family].append(
                (voice_info["name"], voice_key))

        for lang_family in sorted(language_groups.keys()):
            sorted_voices = sorted(
                language_groups[lang_family], key=lambda x: x[0])
            options.extend(sorted_voices)

        return options

    def get_available_languages(self) -> List[str]:
        voices = self.tts_client.get_voices()
        if not voices:
            return []

        languages = set()
        for voice_info in voices.values():
            lang_family = voice_info.get("language", {}).get("family")
            if lang_family:
                languages.add(lang_family)

        return sorted(list(languages))

    def filter_voices_by_language(self, language_family: str) -> List[Tuple[str, str]]:
        voices = self.tts_client.get_voices()
        if not voices:
            return []

        filtered = []
        for voice_key, voice_info in voices.items():
            if voice_info.get("language", {}).get("family") == language_family:
                filtered.append((voice_info["name"], voice_key))

        return sorted(filtered, key=lambda x: x[0])

    def get_voice_info(self, voice_key: str) -> Dict[str, Any]:
        voices = self.tts_client.get_voices()
        return voices.get(voice_key, {})

    def get_speaker_count(self, voice_key: str) -> int:
        voice_info = self.get_voice_info(voice_key)
        return voice_info.get("num_speakers", 1)

    def get_speaker_names(self, voice_key: str) -> List[str]:
        voice_info = self.get_voice_info(voice_key)
        return voice_info.get("speaker_names", [])

    def validate_voice(self, voice_key: str) -> bool:
        voices = self.tts_client.get_voices()
        return voice_key in voices

    def update_settings(self, **kwargs) -> Dict[str, Any]:
        for key, value in kwargs.items():
            if key in self.current_settings and value is not None:
                if key == "voice" and self.validate_voice(value):
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

    def generate_speech_audio(self, text: str, ai_message: str = None) -> Optional[str]:
        text_to_speak = text if text and text.strip() else ai_message
        if not text_to_speak or not text_to_speak.strip():
            return None

        try:
            settings = self.get_current_settings()
            current_voice = settings.get("voice")

            if not current_voice or not self.validate_voice(current_voice):
                voice_options = self.get_voice_options()
                if voice_options:
                    current_voice = voice_options[0][1]
                    self.update_settings(voice=current_voice)
                else:
                    print("No voices available")
                    return None

            audio_file = self.tts_client.synthesize_speech(
                text=text_to_speak,
                voice_key=current_voice,
                speaker_id=settings.get("speaker", 0),
                speed=settings.get("speed", 1.0),
                noise_scale=settings.get("noise_scale", 0.667),
                noise_scale_w=settings.get("noise_scale_w", 0.8)
            )

            return audio_file

        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

    def test_voice_settings(self, voice_key: str = None, speaker_id: int = None,
                            speed: float = None, noise_scale: float = None,
                            noise_scale_w: float = None) -> Optional[str]:
        test_voice = voice_key if voice_key is not None else self.current_settings.get(
            "voice")
        test_speaker = speaker_id if speaker_id is not None else self.current_settings.get(
            "speaker", 0)
        test_speed = speed if speed is not None else self.current_settings.get(
            "speed", 1.0)
        test_noise_scale = noise_scale if noise_scale is not None else self.current_settings.get(
            "noise_scale", 0.667)
        test_noise_scale_w = noise_scale_w if noise_scale_w is not None else self.current_settings.get(
            "noise_scale_w", 0.8)

        if not self.validate_voice(test_voice):
            return None

        test_text = "سلام من یک موتور سخن‌گو پارسی هستم."

        try:
            return self.tts_client.synthesize_speech(
                text=test_text,
                voice_key=test_voice,
                speaker_id=test_speaker,
                speed=test_speed,
                noise_scale=test_noise_scale,
                noise_scale_w=test_noise_scale_w
            )
        except Exception as e:
            print(f"Error testing voice settings: {e}")
            return None
