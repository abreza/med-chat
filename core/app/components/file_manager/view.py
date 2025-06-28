from typing import Dict, List, Any
from app.utils.static import assets
from app.utils.template_engine import template_engine


def generate_file_item_html(file_info: Dict[str, Any], file_id: str, is_selected: bool) -> str:
    return template_engine.render(
        'file_manager/file_item.html',
        file_info=file_info,
        file_id=file_id,
        is_selected=is_selected
    )


def generate_file_stats_html(file_count: int, selected_count: int) -> str:
    return template_engine.render(
        'file_manager/file_stats.html',
        file_count=file_count,
        selected_count=selected_count
    )


def generate_empty_file_list_html() -> str:
    css_content = assets.load_css("file_manager.css")
    return template_engine.render(
        'file_manager/empty_file_list.html',
        css_content=css_content
    )


def generate_file_list_html(files_data: Dict[str, Any], selected_files: List[str]) -> str:
    if not files_data:
        return generate_empty_file_list_html()
    
    css_content = assets.load_css("file_manager.css")
    return template_engine.render(
        'file_manager/file_list.html',
        css_content=css_content,
        files_data=files_data,
        selected_files=selected_files,
        file_count=len(files_data),
        selected_count=len(selected_files)
    )
