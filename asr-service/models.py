from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class ASRRequest(BaseModel):
    audio_data: str = Field(
        ...,
        description="Base64 encoded audio data",
        example="UklGRnoGAABXQVZFZm10IBAAAAABAAEA..."
    )
    language: Optional[str] = Field(
        None,
        description="Language code for transcription (e.g., 'en', 'fa'). If None, auto-detection is used.",
        example="fa"
    )
    region: Optional[str] = Field(
        None,
        description="Region code for transcription (e.g., 'US', 'IR'). If None, no region is specified.",
        example="IR"
    )
    model: Optional[str] = Field(
        "small",
        description="ASR model to use",
        example="small"
    )


class TranscribeResponse(BaseModel):
    success: bool = Field(description="Operation success status")
    text: str = Field(description="Transcribed text")
    language: Optional[str] = Field(description="Detected language code")
    region: Optional[str] = Field(description="Detected region code")
    confidence: Optional[float] = Field(
        description="Transcription confidence score")
    used_model: str = Field(description="ASR model used for transcription")


class LanguageInfo(BaseModel):
    code: str = Field(description="Language code")
    name: str = Field(description="Language name")
    regions: List[Dict[str, str]] = Field(description="Available regions")


class LanguagesResponse(BaseModel):
    success: bool = Field(description="Operation success status")
    languages: List[LanguageInfo] = Field(description="Available languages")


class ModelInfo(BaseModel):
    name: str = Field(description="Model name")
    size: str = Field(description="Model size description")
    url: str = Field(description="Model download URL")


class ModelsResponse(BaseModel):
    success: bool = Field(description="Operation success status")
    models: Dict[str, ModelInfo] = Field(description="Available models")
    current_model: Optional[str] = Field(description="Currently loaded model")
    cache_size: int = Field(description="Number of cached models")


class ErrorResponse(BaseModel):
    detail: str = Field(description="Error message")
