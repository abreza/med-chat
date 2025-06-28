import base64
from typing import Any


def encode_image_to_base64(image_path: Any) -> str:
    file_path = get_file_path(image_path)
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_file_path(file_path: Any) -> str:
    return file_path.name if hasattr(file_path, 'name') else str(file_path)
