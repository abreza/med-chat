from typing import Dict, List, Any


def generate_file_item_html(file_info: Dict[str, Any], file_id: str, is_selected: bool) -> str:
    file_type = file_info.get('type', 'unknown')
    file_name = file_info.get('name', 'Unknown')
    file_size = file_info.get('size', '0 B')

    icon = get_file_icon(file_type)
    type_color = get_file_type_color(file_type)

    if is_selected:
            selection_style = "border-left: 4px solid #6c757d;"
    else:
        selection_style = ""

    action_buttons = f"""
        <button onclick="removeFile('{file_id}')" 
                style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px; margin-left: 4px;"
                title="Remove file">🗑️</button>
    """

    return f"""
    <div style="border: 1px solid #e1e5e9; border-radius: 6px; margin-bottom: 8px; padding: 10px; {selection_style}">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; flex-grow: 1;">
                <label style="display: flex; align-items: center; cursor: pointer; flex-grow: 1;">
                    <input type="checkbox" data-file-id="{file_id}" {'checked' if is_selected else ''} 
                           onchange="updateSelection('{file_id}', this)" style="margin-right: 8px; transform: scale(1.2);">
                    <span style="font-size: 16px; margin-right: 8px;">{icon}</span>
                    <div>
                        <div style="font-weight: 500; margin-bottom: 2px;">{file_name}</div>
                        <div style="font-size: 11px; color: #666;">
                            <span style="color: {type_color}; font-weight: 500;">{file_type.upper()}</span> • {file_size}
                        </div>
                    </div>
                </label>
            </div>
            <div style="display: flex; gap: 4px; margin-left: 10px;">
                {action_buttons}
            </div>
        </div>
    </div>
    """


def generate_file_stats_html(file_count: int, selected_count: int) -> str:
    return f"""
    <div style="padding: 8px 12px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #007bff;">
        <strong>📂 Managed Files ({file_count})</strong>
        <span style="float: right; font-size: 12px; color: #666;">{selected_count} selected</span>
    </div>
    """


def get_file_icon(file_type: str) -> str:
    icons = {
        'image': '🖼️',
        'text': '📄',
        'unknown': '📎'
    }
    return icons.get(file_type, '📎')


def get_file_type_color(file_type: str) -> str:
    colors = {
        'image': '#28a745',
        'text': '#17a2b8',
        'unknown': '#6c757d'
    }
    return colors.get(file_type, '#6c757d')


def generate_empty_file_list_html() -> str:
    return """
    <div style="padding: 20px; text-align: center; color: #666; margin: 10px 0; border-top: 1px solid #e1e5e9;">
        <p style="margin: 0; font-size: 14px;">📁 No files uploaded</p>
        <p style="margin: 5px 0 0 0; font-size: 12px;">Upload images or text files</p>
    </div>
    """


def generate_file_list_html(files_data: Dict[str, Any], selected_files: List[str]) -> str:
    if not files_data:
        return generate_empty_file_list_html()

    html_parts = ["""<div id="file-manager-container" style="max-height: 400px; overflow-y: auto; border: 1px solid #e1e5e9; border-radius: 8px; padding: 10px;">"""]

    html_parts.append(generate_file_stats_html(
        len(files_data), len(selected_files)))

    for file_id, file_info in files_data.items():
        is_selected = file_id in selected_files
        html_parts.append(generate_file_item_html(file_info, file_id, is_selected))

    html_parts.append("</div>")
    return "".join(html_parts)
