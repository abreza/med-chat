from typing import Dict, Any, List, Optional


def validate_message_input(message_data: Optional[Dict[str, Any]]) -> bool:
    if message_data is None:
        return False

    message_text = message_data.get("text", "").strip()
    message_files = message_data.get("files", [])

    if not message_text and not message_files:
        return False

    return True


def validate_file_type(file_path: str, allowed_extensions: List[str]) -> bool:
    if not file_path:
        return False

    return any(file_path.lower().endswith(ext) for ext in allowed_extensions)


def validate_audio_settings(speed: float, noise_scale: float, noise_scale_w: float) -> bool:
    if not (0.1 <= speed <= 3.0):
        return False

    if not (0.0 <= noise_scale <= 1.0):
        return False

    if not (0.0 <= noise_scale_w <= 1.0):
        return False

    return True


def validate_speaker_id(speaker_id: int, max_speakers: int) -> bool:
    if not isinstance(speaker_id, int):
        return False

    return 0 <= speaker_id < max_speakers


def validate_model_name(model_name: str, available_models: List[str]) -> bool:
    if not model_name or not isinstance(model_name, str):
        return False

    return model_name in available_models
