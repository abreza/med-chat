import gradio as gr
from gradio_medchatinput import MedChatInput

def process_input(user_input):
    if user_input is None:
        return "No input received."
    
    text = user_input.get("text", "")
    files = user_input.get("files", [])
    
    response_parts = []
    
    if text:
        response_parts.append(f"Text received: {text}")
    
    if files:
        response_parts.append(f"Files received: {len(files)} file(s)")
        for i, file_path in enumerate(files):
            response_parts.append(f"  File {i+1}: {file_path}")
    
    if not text and not files:
        response_parts.append("No text or files received.")
    
    return "\n".join(response_parts)


if __name__ == "__main__":
    with gr.Blocks(title="Medical Chat with Voice Input", js=MedChatInput.get_immediate_transcription_js()) as demo:
        chatbot = gr.Chatbot(label="Conversation")
        
        user_input = MedChatInput(
            label="Your message",
            placeholder="Type your message or record audio...",
            sources=["upload", "microphone"],
            auto_transcribe=True,
            transcription_language="fa",
            keep_audio_after_transcribe=False,
            file_types=["image", "audio", "text"],
            max_plain_text_length=2000,
            submit_btn="Send",
            stop_btn=False
        )
        
        transcription_trigger = gr.Textbox(visible=False, elem_id="transcription_trigger")
        transcription_result = gr.Textbox(visible=False, elem_id="transcription_result")
        
        def respond(message, history):
            if message is None:
                return history, {"text": "", "files": []}
            
            response = process_input(message)
            
            user_msg = message.get("text", "")
            if message.get("files"):
                user_msg += f" [+{len(message['files'])} file(s)]"
            
            history.append([user_msg, response])
            
            return history, {"text": "", "files": []}
        
        transcription_trigger.change(
            fn=MedChatInput.transcribe,
            inputs=[transcription_trigger],
            outputs=[transcription_result],
            show_progress=False
        )
        
        user_input.submit(
            respond,
            [user_input, chatbot],
            [chatbot, user_input]
        )
    
    demo.load()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
