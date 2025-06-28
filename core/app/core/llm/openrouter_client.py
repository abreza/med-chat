from openai import OpenAI
from typing import List, Dict, Any
from app.config.settings import Config
from ...utils.error import handle_api_error


class OpenRouterClient:
    def __init__(self):
        self.client = OpenAI(base_url=Config.OPENROUTER_BASE_URL,
                             api_key=Config.OPENROUTER_API_KEY)
        self.current_model = Config.DEFAULT_MODEL

    def generate_response(self, messages: List[Dict[str, Any]]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.current_model,
                messages=[self._get_system_message()] + messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return handle_api_error(e)

    def set_model(self, model_name: str) -> bool:
        from .model_manager import ModelManager
        if ModelManager.is_valid_model(model_name):
            self.current_model = model_name
            return True
        return False

    def get_current_model(self) -> str:
        return self.current_model

    def _get_system_message(self) -> Dict[str, str]:
        return {
            "role": "system",
            "content": """You are an intelligent medical AI assistant specializing in Persian language healthcare support. Your responsibilities include:

- Providing general medical information and answering health-related questions
- Helping users understand symptoms and medical conditions
- Offering guidance on first aid and preventive care
- Providing general recommendations for healthy lifestyle choices
- Analyzing medical images when provided (X-rays, lab results, etc.) and providing general observations

Response Guidelines:
- Keep responses concise and easily understandable
- Respond in fluent and simple Persian language
- Avoid creating unnecessary alarm and respond with compassion and care
- Maintain a helpful and supportive tone throughout conversations
- When analyzing images, provide general observations but always recommend consulting with healthcare professionals for definitive diagnosis
- For medical images, describe what you can observe but emphasize the importance of professional medical interpretation"""
        }
