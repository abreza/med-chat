import gradio as gr
from typing import Tuple, List

from app.core.llm.openrouter_client import OpenRouterClient
from ...core.llm.model_manager import ModelManager
from ...core.audio.asr_config import get_region_options, update_language_config
from ...core.audio.tts_manager import TTSManager


class SettingsHandlers:
    def __init__(self, tts_manager: TTSManager, llm_client: OpenRouterClient):
        self.tts_manager = tts_manager
        self.llm_client = llm_client

    def handle_model_change(self, model_name: str) -> str:
        self.llm_client.set_model(model_name)
        vision_capable = ModelManager.is_vision_capable(model_name)
        vision_html = f"🔍 Vision Support: {'Yes' if vision_capable else 'No'}"
        return vision_html

    def handle_language_change(self, language: str) -> gr.update:
        regions, default_region, is_visible = get_region_options(language)
        update_language_config(language, default_region)
        return gr.update(choices=regions, value=default_region, visible=is_visible)

    def handle_region_change(self, language: str, region: str) -> None:
        update_language_config(language, region)

    def handle_tts_language_filter_change(self, language_filter: str) -> gr.update:
        if language_filter == "All Languages":
            filtered_voices = self.tts_manager.get_voice_options()
        else:
            filtered_voices = self.tts_manager.filter_voices_by_language(
                language_filter)

        if filtered_voices:
            default_voice = filtered_voices[0][1]
            return gr.update(choices=filtered_voices, value=default_voice)
        return gr.update(choices=self.tts_manager.get_voice_options())

    def handle_tts_voice_change(self, voice_key: str) -> Tuple[gr.update, str]:
        if not voice_key:
            return gr.update(), ""

        self.tts_manager.update_settings(voice=voice_key)
        speaker_update, speaker_info_text = self._get_speaker_options_update(
            voice_key)
        return speaker_update, speaker_info_text

    def handle_tts_settings_update(self, voice_key: str, speaker_id: int, speed: float,
                                   noise_scale: float, noise_scale_w: float) -> None:
        if not self.tts_manager.validate_voice(voice_key):
            return

        self.tts_manager.update_settings(
            voice=voice_key, speaker=speaker_id, speed=speed,
            noise_scale=noise_scale, noise_scale_w=noise_scale_w
        )

    def _get_speaker_options_update(self, voice_key: str) -> Tuple[gr.update, str]:
        if not voice_key or not self.tts_manager.validate_voice(voice_key):
            return gr.update(maximum=0, value=0, visible=False), ""

        speaker_count = self.tts_manager.get_speaker_count(voice_key)
        speaker_names = self.tts_manager.get_speaker_names(voice_key)

        if speaker_count > 1:
            if speaker_names:
                info_text = f"Speakers: {', '.join(speaker_names)}"
            else:
                info_text = f"{speaker_count} speakers available (0-{speaker_count-1})"
            return gr.update(maximum=speaker_count-1, value=0, visible=True, info=info_text), info_text
        else:
            return gr.update(maximum=0, value=0, visible=False), "Single speaker voice"

    def get_initial_options(self) -> Tuple[List[Tuple[str, str]], List[str], str]:
        voice_options = self.tts_manager.get_voice_options()
        language_options = ["All Languages"] + \
            self.tts_manager.get_available_languages()
        default_voice = self.tts_manager.current_settings.get("voice")
        return voice_options, language_options, default_voice
