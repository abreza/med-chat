import gradio as gr
from typing import Dict, List, Any
from ...utils.medical import get_medical_file_info, extract_dicom_image, extract_nifti_slice
from ...utils.static import assets


def create_interaction_panel() -> Dict[str, Any]:
    with gr.Column():
        gr.HTML("<h3>🔍 Interaction</h3>")

        file_preview = gr.HTML(
            value=generate_empty_preview_html(),
            elem_id="file_preview",
            label="File Preview"
        )

        with gr.Row(visible=False, elem_id="medical_controls") as medical_controls:
            with gr.Column():
                slice_slider = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=50,
                    step=1,
                    label="Slice",
                    visible=True
                )
                axis_dropdown = gr.Dropdown(
                    choices=[("Axial", 2), ("Coronal", 1), ("Sagittal", 0)],
                    value=2,
                    label="View Axis",
                    visible=True
                )
            with gr.Column():
                window_center = gr.Number(
                    label="Window Center",
                    value=40,
                    visible=True
                )
                window_width = gr.Number(
                    label="Window Width",
                    value=400,
                    visible=True
                )
                apply_windowing_btn = gr.Button(
                    "Apply Windowing",
                    size="sm",
                    visible=True
                )

        with gr.Row():
            explain_btn = gr.Button(
                "📊 Explain Selected Files",
                variant="primary",
                scale=1,
                size="sm",
                interactive=False
            )

            ocr_btn = gr.Button(
                "📝 Extract Text (OCR)",
                variant="secondary",
                scale=1,
                size="sm",
                interactive=False,
                visible=False
            )

        explain_result = gr.HTML(
            value="",
            visible=False,
            elem_id="explain_result"
        )

        ocr_result = gr.HTML(
            value="",
            visible=False,
            elem_id="ocr_result"
        )

    return {
        "file_preview": file_preview,
        "explain_btn": explain_btn,
        "ocr_btn": ocr_btn,
        "explain_result": explain_result,
        "ocr_result": ocr_result,
        "medical_controls": medical_controls,
        "slice_slider": slice_slider,
        "axis_dropdown": axis_dropdown,
        "window_center": window_center,
        "window_width": window_width,
        "apply_windowing_btn": apply_windowing_btn,
    }


def generate_empty_preview_html() -> str:
    css = assets.load_css("interaction_panel.css")
    return f"""
    {css}
    <div class="empty-preview">
        <div class="empty-preview-icon">🔍</div>
        <h4 class="empty-preview-title">No File Selected</h4>
        <p class="empty-preview-subtitle">Select files from the file manager to preview them here</p>
    </div>
    """


def generate_single_file_preview_html(file_info: Dict[str, Any]) -> str:
    css = assets.load_css("interaction_panel.css")
    file_name = file_info.get('name', 'Unknown')
    file_type = file_info.get('type', 'unknown')
    file_size = file_info.get('size', '0 B')

    if file_type == 'medical':
        return generate_medical_file_preview_html(file_info)

    icon = get_file_icon(file_type)
    type_color = get_file_type_color(file_type)

    preview_content = ""
    if file_type == 'text':
        content = file_info.get('content', '')
        if content:
            display_content = content[:1000] + \
                "..." if len(content) > 1000 else content
            preview_content = f"""
            <div class="content-preview">
                <div class="content-preview-header">File Content</div>
                <pre class="content-preview-text">{_escape_html(display_content)}</pre>
            </div>
            """
    elif file_type == 'image':
        file_path = file_info.get('path', '')
        if file_path:
            try:
                import base64
                with open(file_path, 'rb') as f:
                    encoded_image = base64.b64encode(f.read()).decode('utf-8')
                preview_content = f"""
                <div class="image-preview">
                    <div class="image-preview-header">Image Preview</div>
                    <div class="image-preview-container">
                        <img src="data:image/jpeg;base64,{encoded_image}" 
                             alt="{file_name}"
                             class="image-preview-img" />
                    </div>
                </div>
                """
            except Exception:
                preview_content = f"""
                <div class="image-preview">
                    <div class="image-fallback">
                        <div class="image-fallback-icon">{icon}</div>
                        <p class="image-fallback-text">Image preview not available</p>
                    </div>
                </div>
                """

    return f"""
    {css}
    <div class="single-file-preview">
        <div class="file-preview-header">
            <span class="file-preview-icon">{icon}</span>
            <div class="file-preview-info">
                <h4 class="file-preview-name">{file_name}</h4>
                <div class="file-preview-meta">
                    <span class="file-preview-type" style="color: {type_color};">
                        {file_type.upper()} FILE
                    </span>
                    <span class="file-preview-size">{file_size}</span>
                </div>
            </div>
        </div>
        {preview_content}
    </div>
    """


def generate_multiple_files_preview_html(files_data: Dict[str, Any], selected_files: List[str]) -> str:
    css = assets.load_css("interaction_panel.css")
    file_count = len(selected_files)

    file_types = {}
    for file_id in selected_files:
        if file_id in files_data:
            file_info = files_data[file_id]
            file_type = file_info.get('type', 'unknown')
            if file_type not in file_types:
                file_types[file_type] = []
            file_types[file_type].append(file_info)

    files_list_html = ""
    for file_type, files in file_types.items():
        icon = get_file_icon(file_type)
        files_list_html += f"""
        <div class="file-group">
            <h5 class="file-group-header">
                <span class="file-group-icon">{icon}</span>
                {file_type.upper()} Files ({len(files)})
            </h5>
            <ul class="file-group-list">
        """
        for file_info in files:
            file_name = file_info.get('name', 'Unknown')
            file_size = file_info.get('size', '0 B')
            files_list_html += f"""
                <li class="file-group-item">
                    <span class="file-group-name">{file_name}</span>
                    <span class="file-group-size">({file_size})</span>
                </li>
            """
        files_list_html += "</ul></div>"

    return f"""
    {css}
    <div class="multiple-files-preview">
        <div class="files-overview">
            <h4 class="overview-title">📁 Multiple Files Selected</h4>
            <p class="overview-subtitle">{file_count} files ready for interaction</p>
        </div>
        <div class="files-list-container">
            {files_list_html}
        </div>
    </div>
    """


def generate_medical_file_preview_html(file_info: Dict[str, Any]) -> str:
    css = assets.load_css("medical_preview.css")
    file_name = file_info.get('name', 'Unknown')
    file_size = file_info.get('size', '0 B')
    file_path = file_info.get('path', '')

    medical_info = get_medical_file_info(file_path)

    slice_index = file_info.get('slice_index', 50)
    axis = file_info.get('axis', 2)
    window_center = file_info.get('window_center', None)
    window_width = file_info.get('window_width', None)

    preview_image = None
    if medical_info["type"] == "dicom":
        preview_image = extract_dicom_image(
            file_path, window_center, window_width)
    elif medical_info["type"] == "nifti":
        preview_image = extract_nifti_slice(file_path, slice_index, axis)

    icon = "🏥" if medical_info["type"] == "dicom" else "🧠"
    type_color = "#e74c3c" if medical_info["type"] == "dicom" else "#9b59b6"

    info_html = ""
    if medical_info["type"] == "dicom":
        info_html = f"""
        <div class="medical-info">
            <div class="medical-info-row">
                <strong>Patient:</strong> {medical_info.get('patient_name', 'Unknown')}
            </div>
            <div class="medical-info-row">
                <strong>Modality:</strong> {medical_info.get('modality', 'Unknown')}
            </div>
            <div class="medical-info-row">
                <strong>Study Date:</strong> {medical_info.get('study_date', 'Unknown')}
            </div>
            <div class="medical-info-row">
                <strong>Series:</strong> {medical_info.get('series_description', 'Unknown')}
            </div>
            <div class="medical-info-row">
                <strong>Dimensions:</strong> {medical_info.get('rows', 0)} x {medical_info.get('columns', 0)}
            </div>
        </div>
        """
    elif medical_info["type"] == "nifti":
        shape_str = " x ".join(map(str, medical_info.get('shape', [])))
        voxel_str = " x ".join(map(str, medical_info.get('voxel_size', [])))
        info_html = f"""
        <div class="medical-info">
            <div class="medical-info-row">
                <strong>Shape:</strong> {shape_str}
            </div>
            <div class="medical-info-row">
                <strong>Dimensions:</strong> {medical_info.get('dimensions', 0)}D
            </div>
            <div class="medical-info-row">
                <strong>Voxel Size:</strong> {voxel_str}
            </div>
            <div class="medical-info-row">
                <strong>Data Type:</strong> {medical_info.get('data_type', 'Unknown')}
            </div>
            <div class="medical-info-row">
                <strong>Orientation:</strong> {medical_info.get('orientation', 'Unknown')}
            </div>
        </div>
        """

    image_html = ""
    if preview_image:
        image_html = f"""
        <div class="medical-image-preview">
            <div class="medical-image-container">
                <img src="data:image/png;base64,{preview_image}" 
                     alt="{file_name}"
                     class="medical-image"
                     id="medical-preview-image"
                />
            </div>
        </div>
        """
    else:
        image_html = f"""
        <div class="medical-image-preview">
            <div class="medical-image-header">Medical Image Preview</div>
            <div class="medical-image-fallback">
                <div class="medical-fallback-icon">{icon}</div>
                <p class="medical-fallback-text">
                    Medical file loaded<br>
                    <small class="medical-fallback-small">Preview not available</small>
                </p>
            </div>
        </div>
        """

    return f"""
    {css}
    <div class="medical-file-preview" data-file-type="{medical_info['type']}" data-file-path="{file_path}">
        <div class="file-preview-header">
            <span class="file-preview-icon">{icon}</span>
            <div class="file-preview-info">
                <h4 class="file-preview-name">{file_name}</h4>
                <div class="file-preview-meta">
                    <span class="file-preview-type" style="color: {type_color};">
                        {medical_info['type'].upper()} FILE
                    </span>
                    <span class="file-preview-size">{file_size}</span>
                </div>
            </div>
        </div>
        {info_html}
        {image_html}
    </div>
    """


def generate_error_preview_html(error_message: str) -> str:
    css = assets.load_css("medical_preview.css")
    return f"""
    {css}
    <div class="medical-error-preview">
        <div class="medical-error-icon">⚠️</div>
        <h4 class="medical-error-title">Medical File Error</h4>
        <p class="medical-error-message">{error_message}</p>
    </div>
    """


def get_file_icon(file_type: str, subtype: str = '') -> str:
    if file_type == 'medical':
        if subtype == 'dicom':
            return '🏥'
        elif subtype == 'nifti':
            return '🧠'
        else:
            return '⚕️'

    icons = {
        'image': '🖼️',
        'text': '📄',
        'unknown': '📎'
    }
    return icons.get(file_type, '📎')


def get_file_type_color(file_type: str) -> str:
    colors = {
        'image': '#10b981',
        'text': '#3b82f6',
        'medical': '#e11d48',
        'unknown': '#6b7280'
    }
    return colors.get(file_type, '#6b7280')


def get_image_mime_type(file_path: str) -> str:
    file_ext = file_path.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp'
    }
    return mime_types.get(file_ext, 'image/jpeg')


def _escape_html(text: str) -> str:
    return (text.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;'))
