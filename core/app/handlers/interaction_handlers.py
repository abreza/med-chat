import gradio as gr
from typing import Dict, List, Any, Tuple
from ..components.interaction_panel import (
    generate_empty_preview_html,
    generate_single_file_preview_html,
    generate_multiple_files_preview_html,
    generate_medical_file_preview_html,
    get_image_mime_type
)
from app.utils.data import extract_selected_files_for_llm
from app.utils.image import encode_image_to_base64, get_file_path
from app.utils.medical import get_medical_file_info
from app.core.llm.openrouter_client import OpenRouterClient
from app.core.llm.model_manager import ModelManager
from app.utils.template_engine import template_engine


class InteractionHandlers:
    def __init__(self, llm_client: OpenRouterClient = None):
        self.llm_client = llm_client or OpenRouterClient()

    def handle_file_selection_change(self, files_data: Dict[str, Any], selected_files: List[str]) -> Tuple[str, gr.update, gr.update, gr.update, gr.update, gr.update]:
        explain_btn_update = gr.update(interactive=len(selected_files) > 0)

        all_images = self._are_all_files_images(files_data, selected_files)
        ocr_btn_update = gr.update(
            interactive=len(selected_files) > 0 and all_images,
            visible=all_images and len(selected_files) > 0
        )

        medical_controls_update = gr.update(visible=False)
        slice_slider_update = gr.update()
        axis_dropdown_update = gr.update()

        if not selected_files:
            preview_html = generate_empty_preview_html()
        elif len(selected_files) == 1:
            file_id = selected_files[0]
            if file_id in files_data:
                file_info = files_data[file_id]
                file_type = file_info.get('type', 'unknown')

                if file_type == 'medical':
                    medical_controls_update, slice_slider_update, axis_dropdown_update = self._configure_medical_controls(
                        file_info)
                    preview_html = generate_medical_file_preview_html(
                        file_info)
                else:
                    preview_html = generate_single_file_preview_html(file_info)
            else:
                preview_html = generate_empty_preview_html()
        else:
            preview_html = generate_multiple_files_preview_html(
                files_data, selected_files)

        return preview_html, explain_btn_update, ocr_btn_update, medical_controls_update, slice_slider_update, axis_dropdown_update

    def _configure_medical_controls(self, file_info: Dict[str, Any]) -> Tuple[gr.update, gr.update, gr.update]:
        file_path = file_info.get('path', '')

        try:
            medical_info = get_medical_file_info(file_path)

            slice_counts = self._get_slice_counts(medical_info)
            max_slices = max(slice_counts.values()) if slice_counts else 1

            if max_slices <= 1:
                medical_controls_update = gr.update(visible=False)
                slice_slider_update = gr.update()
                axis_dropdown_update = gr.update()
            else:
                medical_controls_update = gr.update(visible=True)

                current_axis = file_info.get('axis', 2)  # Default to axial
                current_max_slices = slice_counts.get(current_axis, max_slices)

                slice_slider_update = gr.update(
                    minimum=0,
                    maximum=max(0, current_max_slices - 1),
                    value=min(file_info.get(
                        'slice_index', current_max_slices // 2), current_max_slices - 1),
                    step=1,
                    visible=True
                )

                available_axes = []
                axis_labels = {0: "Sagittal", 1: "Coronal", 2: "Axial"}
                for axis, count in slice_counts.items():
                    if count > 1:
                        available_axes.append((axis_labels[axis], axis))

                if len(available_axes) > 1:
                    axis_dropdown_update = gr.update(
                        choices=available_axes,
                        value=current_axis,
                        visible=True
                    )
                else:
                    axis_dropdown_update = gr.update(visible=False)

        except Exception as e:
            print(f"Error configuring medical controls: {e}")
            medical_controls_update = gr.update(visible=False)
            slice_slider_update = gr.update()
            axis_dropdown_update = gr.update()

        return medical_controls_update, slice_slider_update, axis_dropdown_update

    def _get_slice_counts(self, medical_info: Dict[str, Any]) -> Dict[int, int]:
        slice_counts = {}

        if medical_info["type"] == "dicom":
            rows = medical_info.get('rows', 1)
            columns = medical_info.get('columns', 1)
            slice_counts = {
                0: columns,
            }

        elif medical_info["type"] == "nifti":
            shape = medical_info.get('shape', [1, 1, 1])
            if len(shape) >= 3:
                slice_counts = {
                    0: shape[0],
                    1: shape[1],
                    2: shape[2]
                }
            else:
                slice_counts = {0: 1, 1: 1, 2: 1}

        return slice_counts

    def handle_medical_slice_change(self, files_data: Dict[str, Any], selected_files: List[str], slice_value: int, axis: int) -> Tuple[str, gr.update]:
        if len(selected_files) != 1:
            return generate_empty_preview_html(), gr.update()

        file_id = selected_files[0]
        if file_id not in files_data:
            return generate_empty_preview_html(), gr.update()

        file_info = files_data[file_id]
        if file_info.get('type') != 'medical':
            return generate_empty_preview_html(), gr.update()

        file_path = file_info.get('path', '')
        try:
            medical_info = get_medical_file_info(file_path)
            slice_counts = self._get_slice_counts(medical_info)
            max_slices = slice_counts.get(axis, 1)

            slice_value = max(0, min(slice_value, max_slices - 1))

            slider_update = gr.update(
                minimum=0,
                maximum=max(0, max_slices - 1),
                value=slice_value
            )

        except Exception as e:
            print(f"Error updating slice: {e}")
            slider_update = gr.update()

        updated_file_info = file_info.copy()
        updated_file_info['slice_index'] = slice_value
        updated_file_info['axis'] = axis

        return generate_medical_file_preview_html(updated_file_info), slider_update

    def handle_medical_windowing(self, files_data: Dict[str, Any], selected_files: List[str],
                                 window_center: float, window_width: float) -> str:
        if len(selected_files) != 1:
            return generate_empty_preview_html()

        file_id = selected_files[0]
        if file_id not in files_data:
            return generate_empty_preview_html()

        file_info = files_data[file_id]
        if file_info.get('type') != 'medical':
            return generate_empty_preview_html()

        updated_file_info = file_info.copy()
        updated_file_info['window_center'] = window_center
        updated_file_info['window_width'] = window_width

        return generate_medical_file_preview_html(updated_file_info)

    def _are_all_files_images(self, files_data: Dict[str, Any], selected_files: List[str]) -> bool:
        if not selected_files:
            return False

        for file_id in selected_files:
            if file_id in files_data:
                file_info = files_data[file_id]
                if file_info.get('type') != 'image':
                    return False
            else:
                return False
        return True

    def handle_explain_start(self, files_data: Dict[str, Any], selected_files: List[str]) -> Tuple[str, gr.update]:
        if not selected_files:
            return self._generate_error_html("No files selected for analysis."), gr.update(interactive=True)

        loading_html = self._generate_loading_html(
            len(selected_files), "Analyzing")
        return loading_html, gr.update(interactive=False)

    def handle_explain_request(self, files_data: Dict[str, Any], selected_files: List[str]) -> Tuple[str, gr.update]:
        if not selected_files:
            return self._generate_error_html("No files selected for analysis."), gr.update(interactive=True)

        try:
            image_files, text_contents = extract_selected_files_for_llm(
                files_data, selected_files)

            current_model = self.llm_client.get_current_model()
            has_images = len(image_files) > 0
            model_supports_vision = ModelManager.is_vision_capable(
                current_model)

            if has_images and not model_supports_vision:
                return self._generate_error_html(
                    "The current model does not support image analysis. "
                    "Please select a vision-capable model in settings or remove image files."
                ), gr.update(interactive=True)

            message_text = self._prepare_analysis_message(
                files_data, selected_files, text_contents)

            messages = [
                {
                    "role": "user",
                    "content": message_text
                }
            ]

            if has_images and model_supports_vision:
                messages = self._prepare_vision_messages(
                    message_text, image_files)

            response = self.llm_client.generate_response(messages)

            if not response or response.strip() == "":
                return self._generate_error_html("No response received from the AI model."), gr.update(interactive=True)

            return self._generate_success_html(response, len(selected_files), "Analysis"), gr.update(interactive=True)

        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg.lower():
                return self._generate_error_html("API quota exceeded. Please try again later."), gr.update(interactive=True)
            elif "rate_limit" in error_msg.lower():
                return self._generate_error_html("Rate limit exceeded. Please wait and try again."), gr.update(interactive=True)
            else:
                return self._generate_error_html(f"An error occurred during analysis: {error_msg}"), gr.update(interactive=True)

    def handle_ocr_start(self, files_data: Dict[str, Any], selected_files: List[str]) -> Tuple[str, gr.update]:
        if not selected_files:
            return self._generate_error_html("No files selected for OCR."), gr.update(interactive=True)

        if not self._are_all_files_images(files_data, selected_files):
            return self._generate_error_html("OCR is only available for image files."), gr.update(interactive=True)

        loading_html = self._generate_loading_html(
            len(selected_files), "Extracting text")
        return loading_html, gr.update(interactive=False)

    def handle_ocr_request(self, files_data: Dict[str, Any], selected_files: List[str]) -> Tuple[str, gr.update]:
        if not selected_files:
            return self._generate_error_html("No files selected for OCR."), gr.update(interactive=True)

        if not self._are_all_files_images(files_data, selected_files):
            return self._generate_error_html("OCR is only available for image files."), gr.update(interactive=True)

        try:
            current_model = self.llm_client.get_current_model()
            model_supports_vision = ModelManager.is_vision_capable(
                current_model)

            if not model_supports_vision:
                return self._generate_error_html(
                    "The current model does not support image analysis. "
                    "Please select a vision-capable model in settings for OCR functionality."
                ), gr.update(interactive=True)

            image_files, _ = extract_selected_files_for_llm(
                files_data, selected_files)

            if not image_files:
                return self._generate_error_html("No image files found for OCR processing."), gr.update(interactive=True)

            message_text = self._prepare_ocr_message(
                files_data, selected_files)
            messages = self._prepare_vision_messages(message_text, image_files)

            response = self.llm_client.generate_response(messages)

            if not response or response.strip() == "":
                return self._generate_error_html("No text extracted from the images."), gr.update(interactive=True)

            return self._generate_success_html(response, len(selected_files), "OCR"), gr.update(interactive=True)

        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg.lower():
                return self._generate_error_html("API quota exceeded. Please try again later."), gr.update(interactive=True)
            elif "rate_limit" in error_msg.lower():
                return self._generate_error_html("Rate limit exceeded. Please wait and try again."), gr.update(interactive=True)
            else:
                return self._generate_error_html(f"An error occurred during OCR: {error_msg}"), gr.update(interactive=True)

    def _prepare_analysis_message(self, files_data: Dict[str, Any], selected_files: List[str], text_contents: List[str]) -> str:
        file_types = {}
        file_list = []

        for file_id in selected_files:
            if file_id in files_data:
                file_info = files_data[file_id]
                file_name = file_info.get('name', 'Unknown')
                file_type = file_info.get('type', 'unknown')

                if file_type not in file_types:
                    file_types[file_type] = 0
                file_types[file_type] += 1

                file_list.append(f"- {file_name} ({file_type})")

        message_parts = [
            "Please analyze and explain the following files:",
            "",
            "Files to analyze:",
        ]
        message_parts.extend(file_list)
        message_parts.append("")

        if text_contents:
            message_parts.append("=== TEXT FILE CONTENTS ===")
            message_parts.extend(text_contents)
            message_parts.append("")

        message_parts.extend([
            "Please provide a comprehensive analysis including:",
            "1. Summary of each file's content and purpose",
            "2. Key findings or important information",
            "3. Technical details if applicable",
            "4. Relationships between files if multiple files are provided",
            "5. Any recommendations or insights",
            "",
            "Please respond in Persian (Farsi) language as this is a medical AI assistant."
        ])

        return "\n".join(message_parts)

    def _prepare_ocr_message(self, files_data: Dict[str, Any], selected_files: List[str]) -> str:
        file_list = []

        for file_id in selected_files:
            if file_id in files_data:
                file_info = files_data[file_id]
                file_name = file_info.get('name', 'Unknown')
                file_list.append(f"- {file_name}")

        message_parts = [
            "Please extract all text content from the following image(s) using OCR (Optical Character Recognition):",
            "",
            "Images to process:",
        ]
        message_parts.extend(file_list)
        message_parts.extend([
            "",
            "Please:",
            "1. Extract all visible text from each image accurately",
            "2. Maintain the original formatting and structure as much as possible",
            "3. If there are multiple images, clearly separate the text from each image",
            "4. Include any headers, titles, captions, or labels found in the images",
            "5. If text is unclear or partially obscured, indicate this with [unclear] or [partially visible]",
            "6. Preserve any special formatting like bullet points, numbers, or tables",
            "",
            "Output the extracted text in a clear, readable format. If no text is found in an image, please state 'No text detected in this image'."
        ])

        return "\n".join(message_parts)

    def _prepare_vision_messages(self, text_content: str, image_files: List) -> List[Dict[str, Any]]:
        content_parts = [
            {
                "type": "text",
                "text": text_content
            }
        ]

        if image_files:
            for image_file in image_files:
                try:
                    file_path = get_file_path(image_file)
                    base64_image = encode_image_to_base64(file_path)

                    if base64_image:
                        mime_type = get_image_mime_type(file_path)
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        })
                except Exception as e:
                    print(f"Error processing image {file_path}: {e}")
                    continue

        messages = [
            {
                "role": "user",
                "content": content_parts
            }
        ]

        return messages

    def _generate_loading_html(self, file_count: int, action: str = "Processing") -> str:
        action_text = action.lower()
        action_display = action

        return template_engine.render(
            'handlers/loading.html',
            file_count=file_count,
            action=action,
            action_text=action_text,
            action_display=action_display
        )

    def _generate_success_html(self, response: str, file_count: int, action: str = "Processing") -> str:
        return template_engine.render(
            'handlers/success.html',
            response=response,
            file_count=file_count,
            action=action
        )

    def _generate_error_html(self, error_message: str) -> str:
        return template_engine.render(
            'handlers/error.html',
            error_message=error_message
        )
