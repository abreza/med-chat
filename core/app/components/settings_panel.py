import gradio as gr
from typing import Dict, Any, List, Tuple
from app.config.constants import AVAILABLE_MODELS
from app.config.settings import Config
from app.core.llm.model_manager import ModelManager


def create_llm_settings() -> Dict[str, Any]:
    with gr.Accordion("🧠 AI Model (OpenRouter)", open=True):
        llm_model_dropdown = gr.Dropdown(choices=AVAILABLE_MODELS, value=Config.DEFAULT_MODEL,
                                         label="LLM Model", info="Choose AI model for responses")
        vision_status = gr.HTML(
            value=f"🔍 Vision Support: {'Yes' if ModelManager.is_vision_capable(Config.DEFAULT_MODEL) else 'No'}",
            elem_id="vision_status")
        change_llm_btn = gr.Button("Apply LLM Model", size="sm")

    return {"llm_model_dropdown": llm_model_dropdown, "vision_status": vision_status, "change_llm_btn": change_llm_btn}


def create_asr_settings(language_options: List[Tuple[str, str]], default_language: str = "fa", default_region: str = None) -> Dict[str, Any]:
    with gr.Accordion("🎙️ Speech Recognition", open=False):
        language_dropdown = gr.Dropdown(
            choices=language_options, value=default_language, label="Language", info="Speech recognition language")
        region_dropdown = gr.Dropdown(
            choices=[], value=default_region, label="Region", visible=False, info="Regional variant")

    return {"language_dropdown": language_dropdown, "region_dropdown": region_dropdown}


def create_tts_settings(language_options: List[str], voice_options: List[Tuple[str, str]], default_voice: str = None) -> Dict[str, Any]:
    with gr.Accordion("🔊 Text-to-Speech (Piper)", open=False):
        tts_language_filter = gr.Dropdown(choices=language_options, value="All Languages",
                                          label="Filter by Language", info="Filter voices by language family")
        tts_voice_dropdown = gr.Dropdown(
            choices=voice_options, value=default_voice, label="Voice Model", info="Piper TTS voice to use")

        with gr.Row():
            tts_speaker_slider = gr.Slider(minimum=0, maximum=10, value=0, step=1,
                                           label="Speaker ID", info="For multi-speaker models", visible=False)
            tts_speed_slider = gr.Slider(
                minimum=0.1, maximum=3.0, value=1.0, step=0.1, label="Speed", info="Speech speed multiplier")

        with gr.Row():
            tts_noise_scale_slider = gr.Slider(
                minimum=0.0, maximum=1.0, value=0.667, step=0.01, label="Speech Variability", info="Adds natural variation")
            tts_noise_scale_w_slider = gr.Slider(
                minimum=0.0, maximum=1.0, value=0.8, step=0.01, label="Timing Variability", info="Adds natural timing variation")

        speaker_info = gr.Textbox(label="Speaker Info",
                                  interactive=False, visible=False)

        with gr.Row():
            apply_tts_btn = gr.Button(
                "Apply TTS Settings", variant="primary", scale=2)
            test_tts_btn = gr.Button(
                "Test Voice", variant="secondary", scale=1)

        test_audio = gr.Audio(label="🎵 Voice Test", visible=True)

    return {
        "tts_language_filter": tts_language_filter, "tts_voice_dropdown": tts_voice_dropdown,
        "tts_speaker_slider": tts_speaker_slider, "tts_speed_slider": tts_speed_slider,
        "tts_noise_scale_slider": tts_noise_scale_slider, "tts_noise_scale_w_slider": tts_noise_scale_w_slider,
        "speaker_info": speaker_info, "apply_tts_btn": apply_tts_btn, "test_tts_btn": test_tts_btn, "test_audio": test_audio,
    }


def create_settings_panel(language_options: List[Tuple[str, str]], tts_language_options: List[str],
                          voice_options: List[Tuple[str, str]], default_language: str = "fa",
                          default_region: str = None, default_voice: str = None) -> Dict[str, Any]:
    with gr.Accordion("⚙️ Settings", open=False):
        llm_components = create_llm_settings()
        asr_components = create_asr_settings(
            language_options, default_language, default_region)
        tts_components = create_tts_settings(
            tts_language_options, voice_options, default_voice)

        all_components = {}
        all_components.update(llm_components)
        all_components.update(asr_components)
        all_components.update(tts_components)
        return all_components
