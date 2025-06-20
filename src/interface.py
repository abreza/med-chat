import gradio as gr
from gradio_medchatinput import MedChatInput
from .voice_chat import VoiceChatState
from .llm import generate_ai_response, get_available_models, set_model
from src.audio.tts import (
    create_speech_audio, change_voice_settings, get_current_voice_settings,
    get_voice_info, validate_voice_exists
)
from src.config.asr_settings import language_options, language_to_regions, ASR_MODELS
import src.config.asr_settings as asr_config
import src.config.tts_settings as tts_config
from src.config.tts_settings import (
    piper_voice_options, PIPER_VOICES, get_voice_speaker_count,
    get_voice_speaker_names, filter_voices_by_language, get_available_languages
)
from src.config.base_settings import OPENROUTER_MODEL


def update_regions(language):
    if not language:
        return [], None, False

    if language in language_to_regions:
        regions = language_to_regions[language]
        regions.sort(key=lambda x: x[0])
        default_value = regions[0][1] if regions else None
        return regions, default_value, True
    return [], None, False


def update_speaker_options(voice_key):
    if not voice_key or voice_key not in PIPER_VOICES:
        return gr.update(maximum=0, value=0, visible=False), ""

    speaker_count = get_voice_speaker_count(voice_key)
    speaker_names = get_voice_speaker_names(voice_key)

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


def filter_voices_by_selected_language(language_filter):
    if not language_filter or language_filter == "All Languages":
        return piper_voice_options

    filtered_voices = filter_voices_by_language(language_filter)
    return filtered_voices


def send_message(message_data, state: VoiceChatState):
    if message_data is None:
        return state.get_conversation_display(), state, None, {"text": "", "files": []}
    
    message_text = message_data.get("text", "").strip()
    message_files = message_data.get("files", [])
    
    if not message_text:
        return state.get_conversation_display(), state, None, {"text": "", "files": []}

    state.add_message("user", message_text)

    messages = state.get_messages_for_api()
    ai_response = generate_ai_response(messages)

    state.add_message("assistant", ai_response)

    audio_file = create_speech_audio(ai_response)

    return state.get_conversation_display(), state, audio_file, {"text": "", "files": []}


def reset_conversation(state: VoiceChatState):
    state.clear_conversation()
    return [], state, None



def change_llm_model(model_name):
    success = set_model(model_name)
    if success:
        return f"LLM Model changed to: {model_name}"
    else:
        return f"Failed to change model to: {model_name}"


def update_language_settings(language, region):
    asr_config.current_language = language
    asr_config.current_region = region

    lang_info = "Auto-detect" if not language else language
    region_info = f" ({region})" if region else ""
    status = f"Language set to: {lang_info}{region_info}"

    return status


def update_tts_voice(voice_key):
    if validate_voice_exists(voice_key):
        settings = change_voice_settings(voice=voice_key)
        voice_info = get_voice_info(voice_key)
        status = f"TTS Voice changed to: {voice_info.get('name', voice_key)}"
        return status
    else:
        return f"Invalid voice: {voice_key}"


def update_tts_settings(voice_key, speaker_id, speed, noise_scale, noise_scale_w):
    if not validate_voice_exists(voice_key):
        return f"Invalid voice: {voice_key}"

    settings = change_voice_settings(
        voice=voice_key,
        speaker=speaker_id,
        speed=speed,
        noise_scale=noise_scale,
        noise_scale_w=noise_scale_w
    )

    voice_info = get_voice_info(voice_key)
    status = f"TTS Settings updated - Voice: {voice_info.get('name', voice_key)}, Speed: {speed:.1f}x"
    return status


def test_tts_voice(voice_key, speaker_id, speed, noise_scale, noise_scale_w):
    if not validate_voice_exists(voice_key):
        return None

    original_settings = get_current_voice_settings()
    change_voice_settings(
        voice=voice_key,
        speaker=speaker_id,
        speed=speed,
        noise_scale=noise_scale,
        noise_scale_w=noise_scale_w
    )

    test_text = f"سلام من یک موتور سخن‌گو پارسی هستم.."
    audio_file = create_speech_audio(test_text)

    change_voice_settings(**original_settings)

    return audio_file


immediate_transcription_js = """
function() {
    console.log("Setting up immediate transcription...");
    
    // Set up global transcription function
    window.transcribeAudioImmediate = function(base64Audio) {
        return new Promise((resolve) => {
            // Find the hidden input and output elements
            const triggerEl = document.getElementById('transcription_trigger').querySelector('textarea, input');
            const resultEl = document.getElementById('transcription_result').querySelector('textarea, input');
            
            if (!triggerEl || !resultEl) {
                console.error('Could not find transcription elements');
                resolve('');
                return;
            }
            
            // Set up listener for result
            const originalValue = resultEl.value;
            let checkCount = 0;
            const maxChecks = 500; // 50 seconds timeout
            
            const checkForResult = () => {
                checkCount++;
                if (resultEl.value !== originalValue && resultEl.value !== '') {
                    const result = resultEl.value;
                    resolve(result);
                } else if (checkCount < maxChecks) {
                    setTimeout(checkForResult, 100);
                } else {
                    console.warn('Transcription timeout');
                    resolve('');
                }
            };
            
            // Trigger transcription
            triggerEl.value = base64Audio;
            triggerEl.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Start checking for result
            setTimeout(checkForResult, 100);
        });
    };
    
    console.log("Immediate transcription setup complete");
}
"""


def create_interface():
    with gr.Blocks(title="Voice AI Assistant", theme=gr.themes.Soft(), js=immediate_transcription_js) as demo:
        state = gr.State(value=VoiceChatState())

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="💬 Conversation",
                    height=400,
                    show_copy_button=True
                )

                user_input = MedChatInput(
                    label="Your message",
                    placeholder="Type your message or record audio...",
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
                
                transcription_trigger = gr.Textbox(visible=False, elem_id="transcription_trigger")
                transcription_result = gr.Textbox(visible=False, elem_id="transcription_result")
                
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
                    value=f"Ready",
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

        def on_send_message(message_data, state):
            if message_data is None or not message_data.get("text", "").strip():
                return state.get_conversation_display(), state, None, {"text": "", "files": []}, "Please enter a message"

            chat_history, new_state, audio, cleared_input = send_message(message_data, state)
            return chat_history, new_state, audio, cleared_input, "Message sent successfully"

        def on_llm_model_change(model_name):
            status = change_llm_model(model_name)
            return status

        def on_tts_language_filter_change(language_filter):
            filtered_voices = filter_voices_by_selected_language(language_filter)
            if filtered_voices:
                default_voice = filtered_voices[0][1]
                return gr.update(choices=filtered_voices, value=default_voice)
            return gr.update(choices=piper_voice_options)

        def on_tts_voice_change(voice_key):
            if not voice_key:
                return "", gr.update(), ""

            status = update_tts_voice(voice_key)
            speaker_update, speaker_info_text = update_speaker_options(voice_key)

            voice_info = get_voice_info(voice_key)
            lang_info = voice_info.get('language', {})
            quality = voice_info.get('quality', 'unknown')

            detailed_status = f"{status}\nQuality: {quality}\nLanguage: {lang_info.get('name_english', 'Unknown')}"

            return detailed_status, speaker_update, speaker_info_text

        def on_apply_tts_settings(voice_key, speaker_id, speed, noise_scale, noise_scale_w):
            status = update_tts_settings(voice_key, speaker_id, speed, noise_scale, noise_scale_w)
            return status

        def on_test_tts(voice_key, speaker_id, speed, noise_scale, noise_scale_w):
            audio = test_tts_voice(voice_key, speaker_id, speed, noise_scale, noise_scale_w)
            return audio

        user_input.submit(
            fn=on_send_message,
            inputs=[user_input, state],
            outputs=[chatbot, state, response_audio, user_input, status_text]
        )

        clear_btn.click(
            fn=reset_conversation,
            inputs=[state],
            outputs=[chatbot, state, response_audio]
        )


        change_llm_btn.click(
            fn=on_llm_model_change,
            inputs=[llm_model_dropdown],
            outputs=[status_text]
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
            fn=on_apply_tts_settings,
            inputs=[
                tts_voice_dropdown, tts_speaker_slider, tts_speed_slider,
                tts_noise_scale_slider, tts_noise_scale_w_slider
            ],
            outputs=[status_text]
        )

        test_tts_btn.click(
            fn=on_test_tts,
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
