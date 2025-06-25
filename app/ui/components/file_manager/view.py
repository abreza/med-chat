from typing import Dict, List, Any
from app.utils.static import assets


def generate_file_item_html(file_info: Dict[str, Any], file_id: str, is_selected: bool) -> str:
    file_type = file_info.get('type', 'unknown')
    file_name = file_info.get('name', 'Unknown')
    file_size = file_info.get('size', '0 B')

    icon = get_file_icon(file_type)
    type_color = get_file_type_color(file_type)

    selection_class = "selected" if is_selected else ""

    return f"""
    <div class="file-item {selection_class}">
        <div class="file-item-content">
            <div class="file-item-main">
                <label class="file-item-label">
                    <input type="checkbox" 
                           data-file-id="{file_id}" 
                           {'checked' if is_selected else ''} 
                           onchange="updateSelection('{file_id}', this)" 
                           class="file-checkbox">
                    <span class="file-icon">{icon}</span>
                    <div class="file-info">
                        <div class="file-name">{file_name}</div>
                        <div class="file-meta">
                            <span class="file-type" style="color: {type_color};">{file_type.upper()}</span> 
                            <span class="file-size">{file_size}</span>
                        </div>
                    </div>
                </label>
            </div>
            <div class="file-actions">
                <button onclick="removeFile('{file_id}')" 
                        class="remove-btn"
                        title="Remove file">🗑️</button>
            </div>
        </div>
    </div>
    """


def generate_file_stats_html(file_count: int, selected_count: int) -> str:
    return f"""
    <div class="file-stats">
        <strong>📂 Managed Files ({file_count})</strong>
        <span class="selected-count">{selected_count} selected</span>
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
        'image': '#10b981',
        'text': '#3b82f6',
        'unknown': '#6b7280'
    }
    return colors.get(file_type, '#6b7280')


def generate_empty_file_list_html() -> str:
    return """
    <div class="empty-file-list">
        <div class="empty-icon">📁</div>
        <p class="empty-title">No files uploaded</p>
        <p class="empty-subtitle">Upload images or text files</p>
    </div>
    """


def generate_file_list_html(files_data: Dict[str, Any], selected_files: List[str]) -> str:
    if not files_data:
        return generate_empty_file_list_html()

    html_parts = [get_file_manager_css(),
                  '<div id="file-manager-container" class="file-manager-container">']

    html_parts.append(generate_file_stats_html(
        len(files_data), len(selected_files)))

    for file_id, file_info in files_data.items():
        is_selected = file_id in selected_files
        html_parts.append(generate_file_item_html(
            file_info, file_id, is_selected))

    html_parts.append("</div>")
    return "".join(html_parts)


def get_file_manager_css() -> str:
    return assets.load_css("file_manager.css")
