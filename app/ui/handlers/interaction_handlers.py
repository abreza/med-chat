import gradio as gr
from typing import Dict, List, Any, Tuple
from ..components.interaction_panel import (
    generate_empty_preview_html,
    generate_single_file_preview_html,
    generate_multiple_files_preview_html
)


class InteractionHandlers:
    def __init__(self):
        pass

    def handle_file_selection_change(self, files_data: Dict[str, Any], selected_files: List[str]) -> Tuple[str, gr.update]:
        explain_btn_update = gr.update(interactive=len(selected_files) > 0)

        if not selected_files:
            preview_html = generate_empty_preview_html()
        elif len(selected_files) == 1:
            file_id = selected_files[0]
            if file_id in files_data:
                file_info = files_data[file_id]
                preview_html = generate_single_file_preview_html(file_info)
            else:
                preview_html = generate_empty_preview_html()
        else:
            preview_html = generate_multiple_files_preview_html(
                files_data, selected_files)

        return preview_html, explain_btn_update

    def handle_explain_request(self, files_data: Dict[str, Any], selected_files: List[str]) -> str:
        if not selected_files:
            return ""

        file_types = {}
        total_files = len(selected_files)

        for file_id in selected_files:
            if file_id in files_data:
                file_info = files_data[file_id]
                file_type = file_info.get('type', 'unknown')
                if file_type not in file_types:
                    file_types[file_type] = 0
                file_types[file_type] += 1

        type_explain = []
        for file_type, count in file_types.items():
            type_explain.append(
                f"{count} {file_type} file{'s' if count > 1 else ''}")

        explain_text = f"Ready to explain {total_files} selected file{'s' if total_files > 1 else ''}: {', '.join(type_explain)}"

        return f"""
        <div style="
            background: #e3f2fd; 
            border: 1px solid #2196f3; 
            border-radius: 8px; 
            padding: 16px; 
            margin: 10px 0;
            color: #1565c0;
        ">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 20px; margin-right: 12px;">📊</span>
                <div>
                    <strong>explain Request</strong><br>
                    <span style="font-size: 14px;">{explain_text}</span>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #bbdefb; font-size: 13px;">
                <em>Note: explain functionality will be implemented in the chat interface.</em>
            </div>
        </div>
        """
