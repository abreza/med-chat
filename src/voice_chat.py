import time
import base64
from typing import List, Optional


class VoiceChatState:
    def __init__(self):
        self.conversation = []
        self.is_recording = False
        self.audio_buffer = []
        self.last_activity = time.time()
        self.response_audio = None

    def add_message(self, role: str, content: str, images: Optional[List[str]] = None):
        message = {
            "role": role,
            "content": content
        }
        if images:
            message["images"] = images
        self.conversation.append(message)

    def get_conversation_display(self):
        formatted_messages = []
        
        for msg in self.conversation:
            if msg["role"] == "user":
                content = msg["content"] or ""
                images = msg.get("images", [])
                
                if images:
                    for img_path in images:
                        try:
                            if hasattr(img_path, 'name'):
                                file_path = img_path.name
                            else:
                                file_path = str(img_path)
                            
                            formatted_messages.append({
                                "role": "user", 
                                "content": (file_path,)
                            })
                        except Exception as e:
                            print(f"Error processing image {img_path}: {e}")
                    
                    if content.strip():
                        formatted_messages.append({
                            "role": "user",
                            "content": content
                        })
                else:
                    formatted_messages.append({
                        "role": "user",
                        "content": content
                    })
            else:
                formatted_messages.append({
                    "role": "assistant",
                    "content": msg["content"]
                })
        
        return formatted_messages

    def clear_conversation(self):
        self.conversation = []

    def get_messages_for_api(self):
        formatted_messages = []
        
        for msg in self.conversation:
            if msg["role"] == "user" and msg.get("images"):
                content_parts = []
                
                if msg["content"]:
                    content_parts.append({
                        "type": "text",
                        "text": msg["content"]
                    })
                
                for img_path in msg["images"]:
                    try:
                        base64_image = self._encode_image(img_path)
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

    def _encode_image(self, image_path: str) -> str:
        if hasattr(image_path, 'name'):
            file_path = image_path.name
        else:
            file_path = str(image_path)
            
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
