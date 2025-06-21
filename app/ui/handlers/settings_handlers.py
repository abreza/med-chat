import gradio as gr
from typing import Dict, Any, Tuple, List
from ...core.llm.model_manager import ModelManager
from ...core.audio.speech_recognition.asr_config import get_region_options, update_language_config
from .audio_handlers import AudioHandlers


class SettingsHandlers:
    def __init__(self, audio_handlers: AudioHandlers, llm_client):
        self.audio_handlers = audio_handlers
        self.voice_manager = audio_handlers.get_voice_manager()
        self.llm_client = llm_client

    def handle_model_change(self, model_name: str) -> Tuple[str, str]:
        success = self.llm_client.set_model(model_name)

        vision_capable = ModelManager.is_vision_capable(model_name)
        vision_html = f"🔍 Vision Support: {'Yes' if vision_capable else 'No'}"

        if success:
            status = f"LLM Model changed to: {model_name}\nVision: {'Enabled' if vision_capable else 'Disabled'}"
        else:
            status = f"Failed to change model to: {model_name}"

        return status, vision_html

    def handle_language_change(self, language: str) -> Dict[str, Any]:
        regions, default_region, is_visible = get_region_options(language)
        status = update_language_config(language, default_region)

        return {
            "region_dropdown": gr.update(
                choices=regions,
                value=default_region,
                visible=is_visible
            ),
            "status_text": gr.update(value=status)
        }

    def handle_region_change(self, language: str, region: str) -> str:
        return update_language_config(language, region)

    def handle_tts_language_filter_change(self, language_filter: str) -> gr.update:
        if language_filter == "All Languages":
            filtered_voices = self.voice_manager.get_voice_options()
        else:
            filtered_voices = self.voice_manager.filter_voices_by_language(
                language_filter)

        if filtered_voices:
            default_voice = filtered_voices[0][1]
            return gr.update(choices=filtered_voices, value=default_voice)

        return gr.update(choices=self.voice_manager.get_voice_options())

    def handle_tts_voice_change(self, voice_key: str) -> Tuple[str, gr.update, str]:
        if not voice_key:
            return "", gr.update(), ""

        self.voice_manager.update_settings(voice=voice_key)

        voice_info = self.voice_manager.get_voice_info(voice_key)
        lang_info = voice_info.get('language', {})
        quality = voice_info.get('quality', 'unknown')

        speaker_update, speaker_info_text = self._get_speaker_options_update(
            voice_key)

        status = f"TTS Voice changed to: {voice_info.get('name', voice_key)}\n"
        status += f"Quality: {quality}\n"
        status += f"Language: {lang_info.get('name_english', 'Unknown')}"

        return status, speaker_update, speaker_info_text

    def handle_tts_settings_update(self, voice_key: str, speaker_id: int, speed: float,
                                   noise_scale: float, noise_scale_w: float) -> str:
        if not self.voice_manager.validate_voice(voice_key):
            return f"Invalid voice: {voice_key}"

        settings = self.voice_manager.update_settings(
            voice=voice_key,
            speaker=speaker_id,
            speed=speed,
            noise_scale=noise_scale,
            noise_scale_w=noise_scale_w
        )

        voice_info = self.voice_manager.get_voice_info(voice_key)
        status = f"TTS Settings updated - Voice: {voice_info.get('name', voice_key)}, Speed: {speed:.1f}x"

        return status

    def _get_speaker_options_update(self, voice_key: str) -> Tuple[gr.update, str]:
        if not voice_key or not self.voice_manager.validate_voice(voice_key):
            return gr.update(maximum=0, value=0, visible=False), ""

        speaker_count = self.voice_manager.get_speaker_count(voice_key)
        speaker_names = self.voice_manager.get_speaker_names(voice_key)

        if speaker_count > 1:
            if speaker_names:
                info_text = f"Speakers: {', '.join(speaker_names)}"
            else:
                info_text = f"{speaker_count} speakers available (0-{speaker_count-1})"

            return gr.update(
                maximum=speaker_count-1,
                value=0,
                visible=True,
                info=info_text
            ), info_text
        else:
            return gr.update(maximum=0, value=0, visible=False), "Single speaker voice"

    def get_initial_options(self) -> Tuple[List[Tuple[str, str]], List[str], str]:
        voice_options = self.voice_manager.get_voice_options()
        language_options = ["All Languages"] + \
            self.voice_manager.get_available_languages()
        default_voice = self.voice_manager.current_settings.get("voice")

        return voice_options, language_options, default_voice
