from typing import Dict, Any, Optional


def validate_message_input(message_data: Optional[Dict[str, Any]]) -> bool:
    if message_data is None:
        return False
    message_text = message_data.get("text", "").strip()
    message_files = message_data.get("files", [])
    if not message_text and not message_files:
        return False
    return True
