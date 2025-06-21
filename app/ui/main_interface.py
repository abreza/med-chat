import gradio as gr
from gradio_medchatinput import MedChatInput
from .components.chat_interface import create_chat_interface, setup_transcription_events
from .components.settings_panel import create_settings_panel
from .handlers.chat_handlers import ChatHandlers
from .handlers.audio_handlers import AudioHandlers
from .handlers.settings_handlers import SettingsHandlers
from ..core.config.settings import Config
from ..core.llm.model_manager import ModelManager
from ..core.audio.speech_recognition.asr_config import get_language_options

_audio_handlers = None
_chat_handlers = None
_settings_handlers = None


def create_main_interface():
    global _audio_handlers, _chat_handlers, _settings_handlers
    _audio_handlers = AudioHandlers()
    _chat_handlers = ChatHandlers()
    _settings_handlers = SettingsHandlers(
        _audio_handlers, _chat_handlers.llm_client)

    asr_language_options = get_language_options()
    voice_options, tts_language_options, default_voice = _settings_handlers.get_initial_options()

    with gr.Blocks(
        title="Voice AI Assistant",
        theme=gr.themes.Soft(),
        js=MedChatInput.get_immediate_transcription_js()
    ) as demo:
        conversation_state = gr.State(value=[])
        tts_trigger = gr.State(value="")

        with gr.Row():
            with gr.Column(scale=3):
                chat_components = create_chat_interface()
                setup_transcription_events(chat_components)

            with gr.Column(scale=1):
                settings_components = create_settings_panel(
                    language_options=asr_language_options,
                    tts_language_options=tts_language_options,
                    voice_options=voice_options,
                    default_voice=default_voice
                )

        initial_status = f"Ready - Vision: {'Enabled' if ModelManager.is_vision_capable(Config.DEFAULT_MODEL) else 'Disabled'}"
        chat_components["status_text"].value = initial_status

        _bind_chat_events(chat_components, tts_trigger, conversation_state)
        _bind_settings_events(settings_components, chat_components)

    return demo


def _bind_chat_events(chat_components, tts_trigger, conversation_state):
    def handle_message_step1(message_data, conversation_history):
        global _chat_handlers, _audio_handlers
        chat_history, new_history, cleared_input, status, ai_message = _chat_handlers.handle_message_send_with_history(
            message_data, conversation_history
        )
        return chat_history, new_history, cleared_input, status, ai_message

    def handle_message_step2(ai_message, conversation_history):
        global _audio_handlers
        if ai_message and ai_message.strip():
            return _audio_handlers.generate_speech_audio("", ai_message)
        return None

    chat_components["user_input"].submit(
        fn=handle_message_step1,
        inputs=[chat_components["user_input"], conversation_state],
        outputs=[
            chat_components["chatbot"],
            conversation_state,
            chat_components["user_input"],
            chat_components["status_text"],
            tts_trigger
        ]
    ).then(
        fn=handle_message_step2,
        inputs=[tts_trigger, conversation_state],
        outputs=[chat_components["response_audio"]]
    )

    def handle_clear():
        global _chat_handlers
        return _chat_handlers.handle_conversation_clear_simple()

    chat_components["clear_btn"].click(
        fn=handle_clear,
        inputs=[],
        outputs=[
            chat_components["chatbot"],
            conversation_state,
            chat_components["response_audio"]
        ]
    )


def _bind_settings_events(settings_components, chat_components):
    global _settings_handlers, _audio_handlers

    settings_components["change_llm_btn"].click(
        fn=_settings_handlers.handle_model_change,
        inputs=[settings_components["llm_model_dropdown"]],
        outputs=[chat_components["status_text"],
                 settings_components["vision_status"]]
    )

    settings_components["language_dropdown"].change(
        fn=_settings_handlers.handle_language_change,
        inputs=[settings_components["language_dropdown"]],
        outputs=[settings_components["region_dropdown"],
                 chat_components["status_text"]]
    )

    settings_components["region_dropdown"].change(
        fn=_settings_handlers.handle_region_change,
        inputs=[settings_components["language_dropdown"],
                settings_components["region_dropdown"]],
        outputs=[chat_components["status_text"]]
    )

    settings_components["tts_language_filter"].change(
        fn=_settings_handlers.handle_tts_language_filter_change,
        inputs=[settings_components["tts_language_filter"]],
        outputs=[settings_components["tts_voice_dropdown"]]
    )

    settings_components["tts_voice_dropdown"].change(
        fn=_settings_handlers.handle_tts_voice_change,
        inputs=[settings_components["tts_voice_dropdown"]],
        outputs=[
            chat_components["status_text"],
            settings_components["tts_speaker_slider"],
            settings_components["speaker_info"]
        ]
    )

    settings_components["apply_tts_btn"].click(
        fn=_settings_handlers.handle_tts_settings_update,
        inputs=[
            settings_components["tts_voice_dropdown"],
            settings_components["tts_speaker_slider"],
            settings_components["tts_speed_slider"],
            settings_components["tts_noise_scale_slider"],
            settings_components["tts_noise_scale_w_slider"]
        ],
        outputs=[chat_components["status_text"]]
    )

    settings_components["test_tts_btn"].click(
        fn=_audio_handlers.test_voice_settings,
        inputs=[
            settings_components["tts_voice_dropdown"],
            settings_components["tts_speaker_slider"],
            settings_components["tts_speed_slider"],
            settings_components["tts_noise_scale_slider"],
            settings_components["tts_noise_scale_w_slider"]
        ],
        outputs=[settings_components["test_audio"]]
    )
