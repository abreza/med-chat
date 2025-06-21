from typing import Dict, Any, Tuple, List
from ...core.chat.conversation_manager import ConversationManager
from ...core.llm.openrouter_client import OpenRouterClient
from ...utils.validation import validate_message_input
from ...core.config.constants import SUPPORTED_IMAGE_TYPES


class ChatHandlers:
    def __init__(self):
        self.llm_client = OpenRouterClient()
        self.conversation_manager = ConversationManager(self.llm_client)

    def handle_message_send(self, message_data: Dict[str, Any]) -> Tuple[List, Any, Dict, str, str]:
        if not validate_message_input(message_data):
            return (
                self.conversation_manager.get_conversation_display(),
                self.conversation_manager,
                {"text": "", "files": []},
                "Please enter a message or upload an image",
                ""
            )

        message_text = message_data.get("text", "").strip()
        message_files = message_data.get("files", [])

        image_files = self._extract_image_files(message_files)

        ai_response, success = self.conversation_manager.process_user_input(
            message_text, image_files
        )

        status = "Message sent successfully"
        if image_files:
            image_count = len(image_files)
            status += f" (with {image_count} image{'s' if image_count > 1 else ''})"

        return (
            self.conversation_manager.get_conversation_display(),
            self.conversation_manager,
            {"text": "", "files": []},
            status,
            ai_response if success else ""
        )

    def handle_message_send_with_history(self, message_data: Dict[str, Any], conversation_history: List) -> Tuple[List, List, Dict, str, str]:
        if not validate_message_input(message_data):
            return (
                conversation_history,
                conversation_history,
                {"text": "", "files": []},
                "Please enter a message or upload an image",
                ""
            )

        message_text = message_data.get("text", "").strip()
        message_files = message_data.get("files", [])

        image_files = self._extract_image_files(message_files)

        ai_response, success = self.conversation_manager.process_user_input(
            message_text, image_files
        )

        new_display = self.conversation_manager.get_conversation_display()

        status = "Message sent successfully"
        if image_files:
            image_count = len(image_files)
            status += f" (with {image_count} image{'s' if image_count > 1 else ''})"

        return (
            new_display,
            new_display,
            {"text": "", "files": []},
            status,
            ai_response if success else ""
        )

    def handle_conversation_clear(self) -> Tuple[List, Any, None]:
        self.conversation_manager.clear_conversation()
        return [], self.conversation_manager, None

    def handle_conversation_clear_simple(self) -> Tuple[List, List, None]:
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
