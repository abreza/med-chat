from typing import Optional
from ...core.audio.text_to_speech.piper_engine import PiperEngine
from ...core.audio.text_to_speech.voice_manager import VoiceManager
from ...core.audio.text_to_speech.tts_config import TTSConfig
from ...core.config.settings import Config


class AudioHandlers:
    def __init__(self):
        self.tts_config = TTSConfig(
            data_dir=Config.DATA_DIR, model_dir=Config.TTS_MODEL_DIR)
        self.voice_manager = VoiceManager(self.tts_config)
        self.piper_engine = PiperEngine(
            Config.TTS_MODEL_DIR, self.voice_manager.voices)

    def generate_speech_audio(self, text: str, ai_message: str = None) -> Optional[str]:
        text_to_speak = text if text and text.strip() else ai_message
        if not text_to_speak or not text_to_speak.strip():
            return None
        try:
            settings = self.voice_manager.get_current_settings()
            current_voice = settings.get("voice")
            if not current_voice or not self.voice_manager.validate_voice(current_voice):
                voice_options = self.voice_manager.get_voice_options()
                if voice_options:
                    current_voice = voice_options[0][1]
                    self.voice_manager.update_settings(voice=current_voice)
                else:
                    return None

            audio_file = self.piper_engine.synthesize_speech(
                text=text_to_speak, voice_key=current_voice, speaker_id=settings.get(
                    "speaker", 0),
                speed=settings.get("speed", 1.0), noise_scale=settings.get("noise_scale", 0.667),
                noise_scale_w=settings.get("noise_scale_w", 0.8)
            )
            return audio_file
        except Exception:
            return None

    def test_voice_settings(self, voice_key: str, speaker_id: int, speed: float, noise_scale: float, noise_scale_w: float) -> Optional[str]:
        if not self.voice_manager.validate_voice(voice_key):
            return None
        original_settings = self.voice_manager.get_current_settings()
        self.voice_manager.update_settings(
            voice=voice_key, speaker=speaker_id, speed=speed, noise_scale=noise_scale, noise_scale_w=noise_scale_w)
        test_text = "سلام من یک موتور سخن‌گو پارسی هستم."
        audio_file = self.piper_engine.synthesize_speech(
            text=test_text, voice_key=voice_key, speaker_id=speaker_id, speed=speed, noise_scale=noise_scale, noise_scale_w=noise_scale_w)
        self.voice_manager.update_settings(**original_settings)
        return audio_file

    def get_voice_manager(self) -> VoiceManager:
        return self.voice_manager
