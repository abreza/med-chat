import gradio as gr
import base64
from typing import Dict, List, Any
from pathlib import Path
from ...utils.static import assets


def create_interaction_panel() -> Dict[str, Any]:
    with gr.Column():
        gr.HTML("<h3>🔍 Interaction</h3>")

        file_preview = gr.HTML(
            value=generate_empty_preview_html(),
            elem_id="file_preview",
            label="File Preview"
        )

        with gr.Row():
            explain_btn = gr.Button(
                "📊 Explain Selected Files",
                variant="primary",
                scale=1,
                size="sm",
                interactive=False
            )

        explain_result = gr.HTML(
            value="",
            visible=False,
            elem_id="explain_result"
        )

    return {
        "file_preview": file_preview,
        "explain_btn": explain_btn,
        "explain_result": explain_result
    }


def encode_image_to_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception:
        return None


def get_image_mime_type(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    }
    return mime_types.get(extension, 'image/jpeg')


def generate_empty_preview_html() -> str:
    return f"""
    {get_preview_css()}
    <div class="empty-preview">
        <div class="empty-preview-icon">📄</div>
        <h4 class="empty-preview-title">No File Selected</h4>
        <p class="empty-preview-subtitle">Select files from the File Manager to preview them here</p>
    </div>
    """


def generate_single_file_preview_html(file_info: Dict[str, Any]) -> str:
    file_name = file_info.get('name', 'Unknown')
    file_type = file_info.get('type', 'unknown')
    file_size = file_info.get('size', '0 B')
    file_content = file_info.get('content', '')
    file_path = file_info.get('path', '')

    icon = get_preview_icon(file_type)
    type_color = get_preview_type_color(file_type)

    preview_content = ""

    if file_type == 'text' and file_content:
        preview_text = file_content[:500]
        if len(file_content) > 500:
            preview_text += "..."

        preview_content = f"""
        <div class="content-preview">
            <div class="content-preview-header">
                Content Preview ({len(file_content)} characters)
            </div>
            <pre class="content-preview-text">{preview_text}</pre>
        </div>
        """
    elif file_type == 'image' and file_path:
        base64_image = encode_image_to_base64(file_path)

        if base64_image:
            mime_type = get_image_mime_type(file_path)
            preview_content = f"""
            <div class="image-preview">
                <div class="image-preview-header">Image Preview</div>
                <div class="image-preview-container">
                    <img src="data:{mime_type};base64,{base64_image}" 
                         alt="{file_name}"
                         class="image-preview-img"
                    />
                </div>
            </div>
            """
        else:
            preview_content = f"""
            <div class="image-preview">
                <div class="image-preview-header">Image Preview</div>
                <div class="image-fallback">
                    <div class="image-fallback-icon">🖼️</div>
                    <p class="image-fallback-text">
                        Image file ready for analysis<br>
                        <small class="image-fallback-small">Preview not available</small>
                    </p>
                </div>
            </div>
            """

    return f"""
    {get_preview_css()}
    <div class="single-file-preview">
        <div class="file-preview-header">
            <span class="file-preview-icon">{icon}</span>
            <div class="file-preview-info">
                <h4 class="file-preview-name">{file_name}</h4>
                <div class="file-preview-meta">
                    <span class="file-preview-type" style="color: {type_color};">{file_type.upper()}</span>
                    <span class="file-preview-size">{file_size}</span>
                </div>
            </div>
        </div>
        {preview_content}
    </div>
    """


def generate_multiple_files_preview_html(files_data: Dict[str, Any], selected_files: List[str]) -> str:
    if not selected_files:
        return generate_empty_preview_html()

    file_groups = {}
    total_size = 0
    image_count = 0

    for file_id in selected_files:
        if file_id in files_data:
            file_info = files_data[file_id]
            file_type = file_info.get('type', 'unknown')

            if file_type not in file_groups:
                file_groups[file_type] = []
            file_groups[file_type].append(file_info)

            if file_type == 'image':
                image_count += 1

            size_str = file_info.get('size', '0 B')
            try:
                size_parts = size_str.split()
                if len(size_parts) >= 2:
                    value = float(size_parts[0])
                    unit = size_parts[1].upper()
                    multipliers = {'B': 1, 'KB': 1024,
                                   'MB': 1024**2, 'GB': 1024**3}
                    total_size += int(value * multipliers.get(unit, 1))
            except (ValueError, IndexError):
                continue

    if total_size < 1024:
        total_size_str = f"{total_size} B"
    elif total_size < 1024 * 1024:
        total_size_str = f"{total_size / 1024:.1f} KB"
    elif total_size < 1024 * 1024 * 1024:
        total_size_str = f"{total_size / (1024 * 1024):.1f} MB"
    else:
        total_size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"

    image_thumbnails = ""
    if image_count > 0 and image_count <= 4:
        image_files = file_groups.get('image', [])[:4]
        thumbnails_html = []

        for file_info in image_files:
            file_path = file_info.get('path', '')
            file_name = file_info.get('name', 'Unknown')
            base64_image = encode_image_to_base64(file_path)

            if base64_image:
                mime_type = get_image_mime_type(file_path)
                thumbnails_html.append(f"""
                <div class="thumbnail-item">
                    <img src="data:{mime_type};base64,{base64_image}" 
                         alt="{file_name}"
                         title="{file_name}"
                         class="thumbnail-img"
                    />
                </div>
                """)

        if thumbnails_html:
            image_thumbnails = f"""
            <div class="thumbnails-section">
                <div class="thumbnails-header">Image Thumbnails</div>
                <div class="thumbnails-container">
                    {''.join(thumbnails_html)}
                </div>
            </div>
            """

    files_list_html = ""
    for file_type, files in file_groups.items():
        icon = get_preview_icon(file_type)
        type_color = get_preview_type_color(file_type)

        files_list_html += f"""
        <div class="file-group">
            <h5 class="file-group-header">
                <span class="file-group-icon">{icon}</span>
                <span style="color: {type_color};">{file_type.upper()} Files ({len(files)})</span>
            </h5>
            <ul class="file-group-list">
        """

        for file_info in files:
            file_name = file_info.get('name', 'Unknown')
            file_size = file_info.get('size', '0 B')
            files_list_html += f"""
                <li class="file-group-item">
                    <strong class="file-group-name">{file_name}</strong>
                    <span class="file-group-size">({file_size})</span>
                </li>
            """

        files_list_html += "</ul></div>"

    return f"""
    {get_preview_css()}
    <div class="multiple-files-preview">
        <div class="files-overview">
            <h4 class="overview-title">📁 Selected Files Overview</h4>
            <p class="overview-subtitle">
                {len(selected_files)} files selected • Total size: {total_size_str}
            </p>
        </div>
        
        {image_thumbnails}
        
        <div class="files-list-container">
            {files_list_html}
        </div>
    </div>
    """


def get_preview_icon(file_type: str) -> str:
    icons = {
        'image': '🖼️',
        'text': '📄',
        'unknown': '📎'
    }
    return icons.get(file_type, '📎')


def get_preview_type_color(file_type: str) -> str:
    colors = {
        'image': '#10b981',
        'text': '#3b82f6',
        'unknown': '#6b7280'
    }
    return colors.get(file_type, '#6b7280')


def get_preview_css() -> str:
    return assets.load_css("interaction_panel.css")
