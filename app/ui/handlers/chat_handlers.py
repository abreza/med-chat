from typing import Dict, List, Any, Tuple
from ...core.chat.conversation_manager import ConversationManager
from ...core.llm.openrouter_client import OpenRouterClient
from ...utils.validation import validate_message_input
from ...core.config.constants import SUPPORTED_IMAGE_TYPES
from ...utils.data import extract_selected_files_for_llm, filter_files_by_type


class ChatHandlers:
    def __init__(self):
        self.llm_client = OpenRouterClient()
        self.conversation_manager = ConversationManager(self.llm_client)

    def handle_message_send(self, message_data: Dict[str, Any], conversation_history: List,
                            files_data: Dict = None, selected_files: List[str] = None) -> Tuple[List, List, Dict, str]:
        if not validate_message_input(message_data) and not selected_files:
            return (conversation_history, conversation_history, {"text": "", "files": []}, "")

        message_text = message_data.get("text", "").strip()
        message_files = message_data.get("files", [])
        chat_image_files = self._extract_image_files(message_files)
        managed_image_files = []

        if files_data and selected_files:
            managed_image_files, managed_text_contents = extract_selected_files_for_llm(
                files_data, selected_files)
            if managed_text_contents:
                text_prefix = "\n".join(managed_text_contents) + "\n---\n"
                message_text = text_prefix + message_text

        all_image_files = chat_image_files + managed_image_files
        ai_response, success = self.conversation_manager.process_user_input(
            message_text, all_image_files)
        new_display = self.conversation_manager.get_conversation_display()

        return (new_display, new_display, {"text": "", "files": []}, ai_response if success else "")

    def handle_conversation_clear(self) -> Tuple[List, List, None]:
        self.conversation_manager.clear_conversation()
        return [], [], None

    def _extract_image_files(self, files: List) -> List:
        if not files:
            return []
        image_files = []
        for file in files:
            if file is not None:
                file_path = file.name if hasattr(file, 'name') else str(file)
                if any(file_path.lower().endswith(ext) for ext in SUPPORTED_IMAGE_TYPES):
                    image_files.append(file)
        return image_files
