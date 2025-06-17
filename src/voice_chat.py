import time


class VoiceChatState:
    def __init__(self):
        self.conversation = []
        self.is_recording = False
        self.audio_buffer = []
        self.last_activity = time.time()
        self.response_audio = None

    def add_message(self, role: str, content: str):
        self.conversation.append({"role": role, "content": content})

    def get_conversation_display(self):
        history = []
        for msg in self.conversation:
            if msg["role"] == "user":
                history.append([msg["content"], None])
            else:
                history.append([None, msg["content"]])
        return history

    def clear_conversation(self):
        self.conversation = []

    def get_messages_for_api(self):
        return self.conversation
