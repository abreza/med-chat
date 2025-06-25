from gradio_medchatinput import MedChatInput
from app.ui.components.chat_interface import create_chat_interface, setup_transcription_events
from app.ui.components.settings_panel import create_settings_panel
from app.ui.components.file_manager.file_manager import create_file_manager, file_manager_js
from app.ui.handlers.chat_handlers import ChatHandlers
from app.ui.handlers.audio_handlers import AudioHandlers
from app.ui.handlers.settings_handlers import SettingsHandlers
from app.ui.handlers.file_manager_handlers import FileManagerHandlers
from app.core.audio.speech_recognition.asr_config import get_language_options


class AppSetup:
    def __init__(self):
        self.audio_handlers = AudioHandlers()
        self.chat_handlers = ChatHandlers()
        self.settings_handlers = SettingsHandlers(
            self.audio_handlers, self.chat_handlers.llm_client)
        self.file_manager_handlers = FileManagerHandlers()

        self.asr_language_options = get_language_options()
        self.voice_options, self.tts_language_options, self.default_voice = self.settings_handlers.get_initial_options()

        self.js = "function(){" + MedChatInput.get_transcription_js() + \
            file_manager_js + "}"

    def create_sidebar_components(self):
        file_manager_components = create_file_manager()
        settings_components = create_settings_panel(
            language_options=self.asr_language_options,
            tts_language_options=self.tts_language_options,
            voice_options=self.voice_options,
            default_voice=self.default_voice
        )
        return file_manager_components, settings_components

    def create_chat_components(self):
        chat_components = create_chat_interface()
        setup_transcription_events(chat_components)
        return chat_components

    def get_handlers(self):
        return {
            'audio_handlers': self.audio_handlers,
            'chat_handlers': self.chat_handlers,
            'settings_handlers': self.settings_handlers,
            'file_manager_handlers': self.file_manager_handlers
        }

    def get_js(self):
        return self.js

    def setup_event_handlers(self, file_manager_components, settings_components, chat_components, conversation_state, tts_trigger):
        def handle_message_step2(ai_message, conversation_history):
            if ai_message and ai_message.strip():
                return self.audio_handlers.generate_speech_audio("", ai_message)
            return None

        chat_components["user_input"].submit(
            fn=self.chat_handlers.handle_message_send,
            inputs=[
                chat_components["user_input"],
                conversation_state,
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"]
            ],
            outputs=[
                chat_components["chatbot"],
                conversation_state,
                chat_components["user_input"],
                tts_trigger
            ]
        ).then(
            fn=handle_message_step2,
            inputs=[tts_trigger, conversation_state],
            outputs=[chat_components["response_audio"]]
        )

        chat_components["clear_btn"].click(
            fn=self.chat_handlers.handle_conversation_clear,
            inputs=[],
            outputs=[
                chat_components["chatbot"],
                conversation_state,
                chat_components["response_audio"]
            ]
        ).then(
            fn=lambda fd, sf: self.file_manager_handlers.handle_js_trigger(
                "", fd, sf),
            inputs=[
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"]
            ],
            outputs=[
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"],
                file_manager_components["file_list"]
            ]
        )

        settings_components["change_llm_btn"].click(
            fn=self.settings_handlers.handle_model_change,
            inputs=[settings_components["llm_model_dropdown"]],
            outputs=[settings_components["vision_status"]]
        )

        settings_components["language_dropdown"].change(
            fn=self.settings_handlers.handle_language_change,
            inputs=[settings_components["language_dropdown"]],
            outputs=[settings_components["region_dropdown"]]
        )

        settings_components["region_dropdown"].change(
            fn=self.settings_handlers.handle_region_change,
            inputs=[settings_components["language_dropdown"],
                    settings_components["region_dropdown"]],
            outputs=[]
        )

        settings_components["tts_language_filter"].change(
            fn=self.settings_handlers.handle_tts_language_filter_change,
            inputs=[settings_components["tts_language_filter"]],
            outputs=[settings_components["tts_voice_dropdown"]]
        )

        settings_components["tts_voice_dropdown"].change(
            fn=self.settings_handlers.handle_tts_voice_change,
            inputs=[settings_components["tts_voice_dropdown"]],
            outputs=[
                settings_components["tts_speaker_slider"],
                settings_components["speaker_info"]
            ]
        )

        settings_components["apply_tts_btn"].click(
            fn=self.settings_handlers.handle_tts_settings_update,
            inputs=[
                settings_components["tts_voice_dropdown"],
                settings_components["tts_speaker_slider"],
                settings_components["tts_speed_slider"],
                settings_components["tts_noise_scale_slider"],
                settings_components["tts_noise_scale_w_slider"]
            ],
            outputs=[]
        )

        settings_components["test_tts_btn"].click(
            fn=self.audio_handlers.test_voice_settings,
            inputs=[
                settings_components["tts_voice_dropdown"],
                settings_components["tts_speaker_slider"],
                settings_components["tts_speed_slider"],
                settings_components["tts_noise_scale_slider"],
                settings_components["tts_noise_scale_w_slider"]
            ],
            outputs=[settings_components["test_audio"]]
        )

        file_manager_components["upload_btn"].click(
            fn=self.file_manager_handlers.handle_file_upload,
            inputs=[
                file_manager_components["file_upload"],
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"]
            ],
            outputs=[
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"],
                file_manager_components["file_list"],
                file_manager_components["file_upload"]
            ]
        )

        file_manager_components["select_all_btn"].click(
            fn=self.file_manager_handlers.handle_select_all_files,
            inputs=[file_manager_components["file_manager_state"]],
            outputs=[
                file_manager_components["selected_files_state"],
                file_manager_components["file_list"],
            ]
        )

        file_manager_components["deselect_all_btn"].click(
            fn=self.file_manager_handlers.handle_deselect_all_files,
            inputs=[file_manager_components["file_manager_state"]],
            outputs=[
                file_manager_components["selected_files_state"],
                file_manager_components["file_list"],
            ]
        )

        file_manager_components["remove_selected_btn"].click(
            fn=self.file_manager_handlers.handle_remove_selected_files,
            inputs=[
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"]
            ],
            outputs=[
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"],
                file_manager_components["file_list"],
            ]
        )

        file_manager_components["js_trigger"].change(
            fn=self.file_manager_handlers.handle_js_trigger,
            inputs=[
                file_manager_components["js_trigger"],
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"]
            ],
            outputs=[
                file_manager_components["file_manager_state"],
                file_manager_components["selected_files_state"],
                file_manager_components["file_list"]
            ]
        )
