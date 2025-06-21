from typing import List
from ..config.constants import AVAILABLE_MODELS, VISION_MODELS


class ModelManager:
    @staticmethod
    def get_available_models() -> List[str]:
        return AVAILABLE_MODELS.copy()

    @staticmethod
    def is_valid_model(model_name: str) -> bool:
        return model_name in AVAILABLE_MODELS

    @staticmethod
    def is_vision_capable(model_name: str) -> bool:
        return model_name in VISION_MODELS

    @staticmethod
    def get_vision_models() -> List[str]:
        return list(VISION_MODELS)

    @staticmethod
    def get_model_display_info(model_name: str) -> str:
        vision_status = "Vision: Yes" if ModelManager.is_vision_capable(
            model_name) else "Vision: No"
        return f"Model: {model_name} | {vision_status}"
