import gradio as gr
from typing import Dict, List, Any
from app.utils.medical import get_medical_file_info, extract_dicom_image, extract_nifti_slice
from app.utils.static import assets
from app.utils.template_engine import template_engine
import base64


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
    css_content = assets.load_css("interaction_panel.css")
    return template_engine.render(
        'interaction/empty_preview.html',
        css_content=css_content
    )


def generate_single_file_preview_html(file_info: Dict[str, Any]) -> str:
    css_content = assets.load_css("interaction_panel.css")
    file_type = file_info.get('type', 'unknown')

    if file_type == 'medical':
        return generate_medical_file_preview_html(file_info)

    preview_content = None

    if file_type == 'text':
        content = file_info.get('content', '')
        if content:
            display_content = content[:1000] + \
                "..." if len(content) > 1000 else content
            preview_content = template_engine.render(
                'interaction/content_preview.html',
                content=display_content
            )
    elif file_type == 'image':
        file_path = file_info.get('path', '')
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    encoded_image = base64.b64encode(f.read()).decode('utf-8')
                preview_content = template_engine.render(
                    'interaction/image_preview.html',
                    encoded_image=encoded_image,
                    file_name=file_info.get('name', 'Unknown')
                )
            except Exception:
                preview_content = template_engine.render(
                    'interaction/image_fallback.html',
                    icon=template_engine._get_file_icon(file_type)
                )

    return template_engine.render(
        'interaction/single_file_preview.html',
        css_content=css_content,
        file_info=file_info,
        preview_content=preview_content
    )


def generate_multiple_files_preview_html(files_data: Dict[str, Any], selected_files: List[str]) -> str:
    css_content = assets.load_css("interaction_panel.css")
    file_count = len(selected_files)

    file_types = {}
    for file_id in selected_files:
        if file_id in files_data:
            file_info = files_data[file_id]
            file_type = file_info.get('type', 'unknown')
            if file_type not in file_types:
                file_types[file_type] = []
            file_types[file_type].append(file_info)

    return template_engine.render(
        'interaction/multiple_files_preview.html',
        css_content=css_content,
        file_count=file_count,
        file_types=file_types
    )


def generate_medical_file_preview_html(file_info: Dict[str, Any]) -> str:
    css_content = assets.load_css("medical_preview.css")
    file_path = file_info.get('path', '')

    try:
        medical_info = get_medical_file_info(file_path)
    except Exception as e:
        return generate_error_preview_html(str(e))

    slice_index = file_info.get('slice_index', 0)
    axis = file_info.get('axis', 2)
    window_center = file_info.get('window_center', None)
    window_width = file_info.get('window_width', None)

    preview_image = None
    if medical_info["type"] == "dicom":
        preview_image = extract_dicom_image(
            file_path, window_center, window_width)
    elif medical_info["type"] == "nifti":
        preview_image = extract_nifti_slice(file_path, slice_index, axis)

    return template_engine.render(
        'interaction/medical_file_preview.html',
        css_content=css_content,
        file_info=file_info,
        medical_info=medical_info,
        slice_index=slice_index,
        axis=axis,
        preview_image=preview_image
    )


def generate_error_preview_html(error_message: str) -> str:
    css_content = assets.load_css("medical_preview.css")
    return template_engine.render(
        'interaction/error_preview.html',
        css_content=css_content,
        error_message=error_message
    )


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
