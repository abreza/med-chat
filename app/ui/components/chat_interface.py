import gradio as gr
from gradio_medchatinput import MedChatInput
from typing import Dict, Any


def create_chat_interface(default_language: str = "fa", default_region: str = None) -> Dict[str, Any]:
    chatbot = gr.Chatbot(label="💬 Conversation", height=400,
                         show_copy_button=True, type="messages")

    user_input = MedChatInput(
        label="Your message",
        placeholder="Type your message, record audio, or upload images...",
        sources=["upload", "microphone"],
        auto_transcribe=True,
        transcription_language=default_language,
        transcription_region=default_region,
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
    clear_btn = gr.Button("Clear Chat", variant="secondary", scale=1)
    response_audio = gr.Audio(label="🔊 AI Response",
                              autoplay=True, visible=True)

    return {
        "chatbot": chatbot, "user_input": user_input, "transcription_trigger": transcription_trigger,
        "transcription_result": transcription_result, "clear_btn": clear_btn,
        "response_audio": response_audio,
    }


def setup_transcription_events(components: Dict[str, Any]) -> None:
    components["transcription_trigger"].change(
        fn=MedChatInput.transcribe,
        inputs=[components["transcription_trigger"]],
        outputs=[components["transcription_result"]],
        show_progress=False
    )
