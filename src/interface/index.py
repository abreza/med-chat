import gradio as gr
from gradio_medchatinput import MedChatInput
from src.voice_chat import VoiceChatState
from src.llm import get_available_models, is_vision_model
from src.audio.tts import get_voice_info
from src.config.asr_settings import language_options
import src.config.asr_settings as asr_config
import src.config.tts_settings as tts_config
from src.config.tts_settings import piper_voice_options, get_available_languages
from src.config.base_settings import OPENROUTER_MODEL
from .handlers import (
    update_regions, update_speaker_options, filter_voices_by_selected_language,
    send_message, generate_tts_for_latest_message, reset_conversation,
    change_llm_model, update_language_settings, update_tts_voice, update_tts_settings,
    test_tts_voice
)


def create_interface():
    with gr.Blocks(title="Voice AI Assistant", theme=gr.themes.Soft(), js=MedChatInput.get_immediate_transcription_js()) as demo:
        state = gr.State(value=VoiceChatState())
        tts_trigger = gr.State(value="")

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="💬 Conversation",
                    height=400,
                    show_copy_button=True,
                    type="messages"
                )

                user_input = MedChatInput(
                    label="Your message",
                    placeholder="Type your message, record audio, or upload images...",
                    sources=["upload", "microphone"],
                    auto_transcribe=True,
                    transcription_language=asr_config.current_language,
                    transcription_region=asr_config.current_region,
                    keep_audio_after_transcribe=False,
                    file_types=["image", "audio", "text"],
                    max_plain_text_length=2000,
                    submit_btn="Send",
                    stop_btn=False,
                    lines=1,
                    max_lines=3
                )

                transcription_trigger = gr.Textbox(
                    visible=False, elem_id="transcription_trigger")
                transcription_result = gr.Textbox(
                    visible=False, elem_id="transcription_result")

                transcription_trigger.change(
                    fn=MedChatInput.transcribe,
                    inputs=[transcription_trigger],
                    outputs=[transcription_result],
                    show_progress=False
                )

                with gr.Row():
                    clear_btn = gr.Button(
                        "Clear Chat", variant="secondary", scale=1)

                response_audio = gr.Audio(
                    label="🔊 AI Response",
                    autoplay=True,
                    visible=True
                )

            with gr.Column(scale=1):
                with gr.Accordion("⚙️ Settings", open=False):

                    gr.HTML("<h4>🧠 AI Model (OpenRouter)</h4>")

                    available_models = get_available_models()
                    llm_model_dropdown = gr.Dropdown(
                        choices=available_models,
                        value=OPENROUTER_MODEL,
                        label="LLM Model",
                        info="Choose AI model for responses"
                    )

                    vision_status = gr.HTML(
                        value=f"🔍 Vision Support: {'Yes' if is_vision_model(OPENROUTER_MODEL) else 'No'}",
                        elem_id="vision_status"
                    )

                    change_llm_btn = gr.Button("Apply LLM Model", size="sm")

                    gr.HTML("<hr>")

                    gr.HTML("<h4>🎙️ Speech Recognition</h4>")
                    language_dropdown = gr.Dropdown(
                        choices=language_options,
                        value=asr_config.current_language,
                        label="Language",
                        info="Speech recognition language"
                    )
                    region_dropdown = gr.Dropdown(
                        choices=[],
                        value=asr_config.current_region,
                        label="Region",
                        visible=False,
                        info="Regional variant"
                    )

                    gr.HTML("<hr>")

                    gr.HTML("<h4>🔊 Text-to-Speech (Piper)</h4>")

                    available_languages = [
                        "All Languages"] + get_available_languages()
                    tts_language_filter = gr.Dropdown(
                        choices=available_languages,
                        value="All Languages",
                        label="Filter by Language",
                        info="Filter voices by language family"
                    )

                    tts_voice_dropdown = gr.Dropdown(
                        choices=piper_voice_options,
                        value=tts_config.current_piper_voice,
                        label="Voice Model",
                        info="Piper TTS voice to use"
                    )

                    with gr.Row():
                        tts_speaker_slider = gr.Slider(
                            minimum=0,
                            maximum=10,
                            value=tts_config.current_piper_speaker,
                            step=1,
                            label="Speaker ID",
                            info="For multi-speaker models",
                            visible=False
                        )

                        tts_speed_slider = gr.Slider(
                            minimum=0.1,
                            maximum=3.0,
                            value=tts_config.current_piper_speed,
                            step=0.1,
                            label="Speed",
                            info="Speech speed multiplier"
                        )

                    with gr.Row():
                        tts_noise_scale_slider = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=tts_config.current_piper_noise_scale,
                            step=0.01,
                            label="Speech Variability",
                            info="Adds natural variation"
                        )

                        tts_noise_scale_w_slider = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=tts_config.current_piper_noise_scale_w,
                            step=0.01,
                            label="Timing Variability",
                            info="Adds natural timing variation"
                        )

                    speaker_info = gr.Textbox(
                        label="Speaker Info",
                        interactive=False,
                        visible=False
                    )

                    with gr.Row():
                        apply_tts_btn = gr.Button(
                            "Apply TTS Settings", variant="primary", scale=2)
                        test_tts_btn = gr.Button(
                            "Test Voice", variant="secondary", scale=1)

                    test_audio = gr.Audio(
                        label="🎵 Voice Test",
                        visible=True
                    )

                status_text = gr.Textbox(
                    label="📊 Status",
                    value=f"Ready - Vision: {'Enabled' if is_vision_model(OPENROUTER_MODEL) else 'Disabled'}",
                    interactive=False,
                    lines=5
                )

        def on_language_change(language):
            regions, default_value, is_visible = update_regions(language)
            status = update_language_settings(language, default_value)
            return {
                region_dropdown: gr.update(
                    choices=regions, value=default_value, visible=is_visible
                ),
                status_text: gr.update(value=status)
            }

        def on_region_change(language, region):
            status = update_language_settings(language, region)
            return gr.update(value=status)

        def on_send_message_step1(message_data, state):
            if message_data is None or (not message_data.get("text", "").strip() and not message_data.get("files", [])):
                return state.get_conversation_display(), state, {"text": "", "files": []}, "Please enter a message or upload an image", ""

            chat_history, new_state, cleared_input, status = send_message(
                message_data, state)

            latest_ai_message = ""
            if new_state.conversation and new_state.conversation[-1]["role"] == "assistant":
                latest_ai_message = new_state.conversation[-1]["content"]

            return chat_history, new_state, cleared_input, status, latest_ai_message

        def on_send_message_step2(ai_message, state):
            if not ai_message or not ai_message.strip():
                return None

            audio_file = generate_tts_for_latest_message(state, ai_message)
            return audio_file

        def on_tts_language_filter_change(language_filter):
            filtered_voices = filter_voices_by_selected_language(
                language_filter)
            if filtered_voices:
                default_voice = filtered_voices[0][1]
                return gr.update(choices=filtered_voices, value=default_voice)
            return gr.update(choices=piper_voice_options)

        def on_tts_voice_change(voice_key):
            if not voice_key:
                return "", gr.update(), ""

            status = update_tts_voice(voice_key)
            speaker_update, speaker_info_text = update_speaker_options(
                voice_key)

            voice_info = get_voice_info(voice_key)
            lang_info = voice_info.get('language', {})
            quality = voice_info.get('quality', 'unknown')

            detailed_status = f"{status}\nQuality: {quality}\nLanguage: {lang_info.get('name_english', 'Unknown')}"

            return detailed_status, speaker_update, speaker_info_text

        def on_model_change(model_name):
            status = change_llm_model(model_name)
            vision_capable = is_vision_model(model_name)
            vision_html = f"🔍 Vision Support: {'Yes' if vision_capable else 'No'}"
            full_status = f"{status}\nVision: {'Enabled' if vision_capable else 'Disabled'}"
            return full_status, vision_html

        user_input.submit(
            fn=on_send_message_step1,
            inputs=[user_input, state],
            outputs=[chatbot, state, user_input, status_text, tts_trigger]
        ).then(
            fn=on_send_message_step2,
            inputs=[tts_trigger, state],
            outputs=[response_audio]
        )

        clear_btn.click(
            fn=reset_conversation,
            inputs=[state],
            outputs=[chatbot, state, response_audio]
        )

        change_llm_btn.click(
            fn=on_model_change,
            inputs=[llm_model_dropdown],
            outputs=[status_text, vision_status]
        )

        language_dropdown.change(
            fn=on_language_change,
            inputs=[language_dropdown],
            outputs=[region_dropdown, status_text]
        )

        region_dropdown.change(
            fn=on_region_change,
            inputs=[language_dropdown, region_dropdown],
            outputs=[status_text]
        )

        tts_language_filter.change(
            fn=on_tts_language_filter_change,
            inputs=[tts_language_filter],
            outputs=[tts_voice_dropdown]
        )

        tts_voice_dropdown.change(
            fn=on_tts_voice_change,
            inputs=[tts_voice_dropdown],
            outputs=[status_text, tts_speaker_slider, speaker_info]
        )

        apply_tts_btn.click(
            fn=update_tts_settings,
            inputs=[
                tts_voice_dropdown, tts_speaker_slider, tts_speed_slider,
                tts_noise_scale_slider, tts_noise_scale_w_slider
            ],
            outputs=[status_text]
        )

        test_tts_btn.click(
            fn=test_tts_voice,
            inputs=[
                tts_voice_dropdown, tts_speaker_slider, tts_speed_slider,
                tts_noise_scale_slider, tts_noise_scale_w_slider
            ],
            outputs=[test_audio]
        )

        demo.load(
            fn=on_language_change,
            inputs=[language_dropdown],
            outputs=[region_dropdown, status_text]
        )

    return demo
