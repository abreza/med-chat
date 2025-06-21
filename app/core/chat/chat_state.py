import time
import base64
from typing import List, Optional, Dict, Any


class ChatState:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.is_recording = False
        self.audio_buffer = []
        self.last_activity = time.time()
        self.current_audio = None

    def add_user_message(self, content: str, images: Optional[List[str]] = None) -> None:
        message = {
            "role": "user",
            "content": content,
            "timestamp": time.time()
        }
        
        if images:
            message["images"] = images
            
        self.messages.append(message)
        self._update_activity()

    def add_assistant_message(self, content: str) -> None:
        message = {
            "role": "assistant", 
            "content": content,
            "timestamp": time.time()
        }
        
        self.messages.append(message)
        self._update_activity()

    def get_display_messages(self) -> List[Dict[str, Any]]:
        display_messages = []
        
        for msg in self.messages:
            if msg["role"] == "user":
                content = msg["content"] or ""
                images = msg.get("images", [])
                
                if images:
                    for img_path in images:
                        try:
                            file_path = self._get_file_path(img_path)
                            display_messages.append({
                                "role": "user",
                                "content": (file_path,)
                            })
                        except Exception as e:
                            print(f"Error processing image {img_path}: {e}")
                
                if content.strip():
                    display_messages.append({
                        "role": "user",
                        "content": content
                    })
            else:
                display_messages.append({
                    "role": "assistant", 
                    "content": msg["content"]
                })
        
        return display_messages

    def get_api_messages(self) -> List[Dict[str, Any]]:
        formatted_messages = []
        
        for msg in self.messages:
            if msg["role"] == "user" and msg.get("images"):
                content_parts = []
                
                if msg["content"]:
                    content_parts.append({
                        "type": "text",
                        "text": msg["content"]
                    })
                
                for img_path in msg["images"]:
                    try:
                        base64_image = self._encode_image_to_base64(img_path)
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        })
                    except Exception as e:
                        print(f"Error encoding image {img_path}: {e}")
                
                formatted_messages.append({
                    "role": msg["role"],
                    "content": content_parts
                })
            else:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return formatted_messages

    def clear_conversation(self) -> None:
        self.messages.clear()
        self.current_audio = None
        self._update_activity()

    def get_latest_assistant_message(self) -> Optional[str]:
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None

    def _update_activity(self) -> None:
        self.last_activity = time.time()

    def _get_file_path(self, file_path: Any) -> str:
        if hasattr(file_path, 'name'):
            return file_path.name
        return str(file_path)

    def _encode_image_to_base64(self, image_path: Any) -> str:
        file_path = self._get_file_path(image_path)
        
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
