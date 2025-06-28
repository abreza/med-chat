import os
from typing import Dict, List, Optional, Union
from pathlib import Path

from app.config.constants import SUPPORTED_IMAGE_TYPES, SUPPORTED_MEDICAL_TYPES, SUPPORTED_TEXT_TYPES


def format_file_size(size_input: Union[int, str, Path]) -> str:
    if isinstance(size_input, (str, Path)):
        try:
            size_bytes = os.path.getsize(size_input)
        except (OSError, TypeError):
            return "0 B"
    else:
        size_bytes = size_input

    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_file_type(file_ext: str) -> Optional[str]:
    file_ext = file_ext.lower()

    if file_ext in SUPPORTED_IMAGE_TYPES:
        return 'image'

    if file_ext in SUPPORTED_MEDICAL_TYPES:
        return 'medical'

    if file_ext in SUPPORTED_TEXT_TYPES:
        return 'text'

    return None


def read_file_content_safe(file_path: Union[str, Path]) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return "Unable to read file content"


def safe_remove_file(file_path: Union[str, Path]) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def create_file_info(file_id: str, original_name: str, file_type: str, file_path: Path, content: Optional[str] = None, subtype: Optional[str] = None) -> Dict:
    file_size = format_file_size(file_path)
    file_info = {
        'name': original_name,
        'type': file_type,
        'path': str(file_path),
        'size': file_size,
        'content': content
    }

    if subtype:
        file_info['subtype'] = subtype

    return file_info


def extract_image_files(files: List, supported_types: List[str]) -> List:
    if not files:
        return []

    image_files = []
    for file in files:
        if file is not None:
            file_path = file.name if hasattr(file, 'name') else str(file)
            if any(file_path.lower().endswith(ext) for ext in supported_types):
                image_files.append(file)
    return image_files


def get_file_extension(filename: str) -> str:
    if filename.lower().endswith('.nii.gz'):
        return '.nii.gz'
    elif '.' in filename:
        return '.' + filename.split('.')[-1].lower()
    return ''


def generate_unique_filename(file_id: str, original_name: str) -> str:
    return f"{file_id}_{original_name}"


def get_filename_from_path(file_path: str) -> str:
    return file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]


def validate_file_type(file_path: str, allowed_extensions: List[str]) -> bool:
    file_ext = get_file_extension(get_filename_from_path(file_path))
    return file_ext in allowed_extensions


def calculate_directory_size(directory_path: Union[str, Path]) -> int:
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    continue
    except Exception:
        pass
    return total_size


def ensure_directory_exists(directory_path: Union[str, Path]) -> bool:
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def is_text_file(file_path: Union[str, Path]) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Try to read first 1KB
        return True
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
        return False


def get_file_stats(file_path: Union[str, Path]) -> Dict[str, any]:
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_file': os.path.isfile(file_path),
            'is_directory': os.path.isdir(file_path),
            'extension': get_file_extension(str(file_path)),
            'filename': get_filename_from_path(str(file_path))
        }
    except (OSError, IOError):
        return {
            'size': 0,
            'size_formatted': '0 B',
            'created': 0,
            'modified': 0,
            'accessed': 0,
            'is_file': False,
            'is_directory': False,
            'extension': '',
            'filename': ''
        }
