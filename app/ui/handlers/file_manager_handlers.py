import json
import uuid
import shutil
from typing import Dict, List, Tuple, Optional
from ...core.config.constants import SUPPORTED_IMAGE_TYPES
from ...core.config.settings import Config
from ..components.file_manager.file_manager import generate_file_list_html
from ...utils.file import get_file_type, read_file_content_safe, safe_remove_file, create_file_info


class FileManagerResponse:
    def __init__(self, files_data: Dict, selected_files: List[str], file_list_html: str,
                 show_image_viewer: bool = False, image_path: Optional[str] = None):
        self.files_data = files_data
        self.selected_files = selected_files
        self.file_list_html = file_list_html
        self.show_image_viewer = show_image_viewer
        self.image_path = image_path

    def to_tuple(self) -> Tuple:
        return (self.files_data, self.selected_files, self.file_list_html,
                self.show_image_viewer, self.image_path)


class FileManagerHandlers:
    def __init__(self):
        self.files_dir = Config.DATA_DIR / "managed_files"
        self.files_dir.mkdir(parents=True, exist_ok=True)

    def _generate_response(self, files_data: Dict, selected_files: List[str], **kwargs) -> FileManagerResponse:
        file_list_html = generate_file_list_html(files_data, selected_files)
        return FileManagerResponse(files_data, selected_files, file_list_html, **kwargs)

    def _process_single_file(self, file) -> Optional[Tuple[str, Dict]]:
        if file is None:
            return None
        try:
            file_id = str(uuid.uuid4())
            original_name = file.name.split(
                '/')[-1] if '/' in file.name else file.name
            file_ext = '.' + \
                original_name.split(
                    '.')[-1].lower() if '.' in original_name else ''
            file_type = get_file_type(file_ext, SUPPORTED_IMAGE_TYPES)
            if not file_type:
                return None

            new_filename = f"{file_id}_{original_name}"
            new_file_path = self.files_dir / new_filename
            shutil.copy2(file.name, new_file_path)

            content = None
            if file_type == 'text':
                content = read_file_content_safe(new_file_path)

            file_info = create_file_info(
                file_id, original_name, file_type, new_file_path, content)
            return file_id, file_info
        except Exception:
            return None

    def handle_file_upload(self, uploaded_files: List, files_data: Dict, selected_files: List[str]) -> Tuple[Dict, List[str], str, None]:
        if not uploaded_files:
            response = self._generate_response(files_data, selected_files)
            return response.files_data, response.selected_files, response.file_list_html, None

        new_files_data = files_data.copy()
        for file in uploaded_files:
            result = self._process_single_file(file)
            if result:
                file_id, file_info = result
                new_files_data[file_id] = file_info
        response = self._generate_response(new_files_data, selected_files)
        return response.files_data, response.selected_files, response.file_list_html, None

    def handle_select_all_files(self, files_data: Dict) -> Tuple[List[str], str]:
        all_file_ids = list(files_data.keys())
        response = self._generate_response(files_data, all_file_ids)
        return response.selected_files, response.file_list_html

    def handle_deselect_all_files(self, files_data: Dict) -> Tuple[List[str], str]:
        response = self._generate_response(files_data, [])
        return response.selected_files, response.file_list_html

    def handle_remove_selected_files(self, files_data: Dict, selected_files: List[str]) -> Tuple[Dict, List[str], str]:
        if not selected_files:
            response = self._generate_response(files_data, selected_files)
            return response.files_data, response.selected_files, response.file_list_html

        new_files_data = files_data.copy()
        for file_id in selected_files:
            if file_id in new_files_data:
                file_path = new_files_data[file_id]['path']
                safe_remove_file(file_path)
                del new_files_data[file_id]
        response = self._generate_response(new_files_data, [])
        return response.files_data, response.selected_files, response.file_list_html

    def handle_close_image_viewer(self, files_data: Dict, selected_files: List[str]) -> Tuple[bool, Optional[str]]:
        return False, None

    def handle_js_trigger(self, trigger_data: str, files_data: Dict, selected_files: List[str]) -> Tuple[Dict, List[str], str, bool, Optional[str]]:
        if not trigger_data or not trigger_data.strip():
            response = self._generate_response(files_data, selected_files)
            return response.to_tuple()

        try:
            data = json.loads(trigger_data)
            action = data.get('action')
            action_data = data.get('data', {})

            action_handlers = {
                'selection_change': self._handle_js_selection_change,
                'remove_file': self._handle_js_remove_file,
            }

            handler = action_handlers.get(action)
            if handler:
                response = handler(action_data, files_data, selected_files)
                return response.to_tuple()
            else:
                response = self._generate_response(files_data, selected_files)
                return response.to_tuple()
        except Exception:
            response = self._generate_response(files_data, selected_files)
            return response.to_tuple()

    def _handle_js_selection_change(self, action_data: Dict, files_data: Dict, selected_files: List[str]) -> FileManagerResponse:
        new_selected_files = action_data.get('allSelected', [])
        return self._generate_response(files_data, new_selected_files)

    def _handle_js_remove_file(self, action_data: Dict, files_data: Dict, selected_files: List[str]) -> FileManagerResponse:
        file_id = action_data.get('fileId')
        if file_id not in files_data:
            return self._generate_response(files_data, selected_files)
        new_files_data = files_data.copy()
        new_selected_files = [fid for fid in selected_files if fid != file_id]
        file_path = new_files_data[file_id]['path']
        safe_remove_file(file_path)
        del new_files_data[file_id]
        return self._generate_response(new_files_data, new_selected_files)
