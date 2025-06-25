import gradio as gr
from typing import Dict, Any
from .view import generate_file_list_html
from app.utils.static import assets


def create_file_manager() -> Dict[str, Any]:
    with gr.Accordion("📁 File Manager (Context Files)", open=True):
        with gr.Column():
            file_upload = gr.File(label="📤 Upload Files", file_count="multiple", file_types=[
                                  "image", "text"], height=200)
            upload_btn = gr.Button(
                "Upload", variant="primary", scale=1, size="sm")

        file_list = gr.HTML(value=generate_file_list_html(
            {}, []), elem_id="file_list")

        with gr.Row():
            select_all_btn = gr.Button(
                "Select All", variant="secondary", scale=1, size="sm")
            deselect_all_btn = gr.Button(
                "Deselect All", variant="secondary", scale=1, size="sm")
            remove_selected_btn = gr.Button(
                "Remove Selected", variant="stop", scale=1, size="sm")

        file_manager_state = gr.State(value={})
        selected_files_state = gr.State(value=[])
        js_trigger = gr.Textbox(visible=False, elem_id="js_trigger")

    return {
        "file_upload": file_upload, "upload_btn": upload_btn, "file_list": file_list,
        "select_all_btn": select_all_btn, "deselect_all_btn": deselect_all_btn, "remove_selected_btn": remove_selected_btn,
        "file_manager_state": file_manager_state,
        "selected_files_state": selected_files_state, "js_trigger": js_trigger,
    }


def get_file_manager_js() -> str:
    return assets.load_js("file_manager.js")
