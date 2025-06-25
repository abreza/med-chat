import gradio as gr
from app_setup import AppSetup

app_setup = AppSetup()

with gr.Blocks(title="Medical AI Assistant", theme=gr.themes.Soft(), js=app_setup.get_js()) as demo:
    conversation_state = gr.State(value=[])
    tts_trigger = gr.State(value="")

    with gr.Row():
        with gr.Column(scale=2):
            file_manager_components, settings_components = app_setup.create_sidebar_components()

        with gr.Column(scale=4):
            chat_components = app_setup.create_chat_components()

    app_setup.setup_event_handlers(
        file_manager_components, settings_components, chat_components,
        conversation_state, tts_trigger
    )

if __name__ == "__main__":
    print("🌐 Launching application...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
