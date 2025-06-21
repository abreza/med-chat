from typing import List, Dict, Any, Optional
from .chat_state import ChatState
from ..llm.openrouter_client import OpenRouterClient


class ConversationManager:
    def __init__(self, llm_client: OpenRouterClient):
        self.llm_client = llm_client
        self.chat_state = ChatState()

    def process_user_input(self, message_text: str, image_files: Optional[List] = None) -> tuple[str, bool]:
        try:
            if not message_text.strip() and not image_files:
                return "Please enter a message or upload an image", False
            self.chat_state.add_user_message(message_text, image_files)
            api_messages = self.chat_state.get_api_messages()
            ai_response = self.llm_client.generate_response(api_messages)
            self.chat_state.add_assistant_message(ai_response)
            return ai_response, True
        except Exception as e:
            error_msg = f"Error processing message: {e}"
            print(error_msg)
            return "عذر می‌خواهم، خطایی رخ داده است. لطفا دوباره تلاش کنید.", False

    def get_conversation_display(self) -> List[Dict[str, Any]]:
        return self.chat_state.get_display_messages()

    def clear_conversation(self) -> None:
        self.chat_state.clear_conversation()

    def get_latest_response(self) -> Optional[str]:
        return self.chat_state.get_latest_assistant_message()
