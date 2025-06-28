from typing import List, Dict, Any, Tuple, Optional
from ..llm.openrouter_client import OpenRouterClient
from app.utils.image import encode_image_to_base64
from app.utils.error import format_error_response


class ConversationManager:
    def __init__(self, llm_client: OpenRouterClient):
        self.llm_client = llm_client
        self.conversation_history = []

    def process_user_input(self, message_text: str, llm_files: List = None,
                           history_files: List = None) -> Tuple[str, bool]:
        try:
            llm_message = self._create_user_message(
                message_text, llm_files or [])

            history_message = self._create_user_message(
                message_text, history_files or [])

            self.conversation_history.append(history_message)

            ai_response = self.llm_client.generate_response(
                self.conversation_history[:-1] + [llm_message]
            )

            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })

            return ai_response, True

        except Exception as e:
            error_message, success = format_error_response(e)

            if message_text.strip():
                history_message = self._create_user_message(
                    message_text, history_files or [])
                self.conversation_history.append(history_message)

                self.conversation_history.append({
                    "role": "assistant",
                    "content": error_message
                })

            return error_message, success

    def _create_user_message(self, text: str, files: List) -> Dict[str, Any]:
        if not files:
            return {"role": "user", "content": text}

        if self.llm_client.get_current_model() and any(files):
            content_parts = []

            if text.strip():
                content_parts.append({"type": "text", "text": text})

            for file in files:
                try:
                    base64_image = encode_image_to_base64(file)
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
                except Exception:
                    continue  # Skip problematic images

            return {"role": "user", "content": content_parts}
        else:
            return {"role": "user", "content": text}

    def get_conversation_display(self) -> List[Dict[str, Any]]:
        display_messages = []

        for message in self.conversation_history:
            if message["role"] == "user":
                content = message["content"]

                if isinstance(content, list):
                    text_parts = []
                    image_files = []

                    for part in content:
                        if part["type"] == "text":
                            text_parts.append(part["text"])
                        elif part["type"] == "image_url":
                            image_files.append(part["image_url"]["url"])

                    display_content = "\n".join(text_parts)
                    if image_files:
                        display_content += f"\n[{len(image_files)} image(s) attached]"

                    display_messages.append(
                        {"role": "user", "content": display_content})
                else:
                    display_messages.append(
                        {"role": "user", "content": content})

            elif message["role"] == "assistant":
                display_messages.append(
                    {"role": "assistant", "content": message["content"]})

        return display_messages

    def clear_conversation(self) -> None:
        self.conversation_history = []

    def get_last_ai_response(self) -> Optional[str]:
        for message in reversed(self.conversation_history):
            if message["role"] == "assistant":
                return message["content"]
        return None

    def get_conversation_length(self) -> int:
        return len(self.conversation_history)

    def export_conversation(self) -> List[Dict[str, Any]]:
        return self.conversation_history.copy()
