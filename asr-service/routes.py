import os
import tempfile
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from models import ASRRequest, TranscribeResponse, LanguagesResponse, ModelsResponse, GeneralResponse
from core import (
    get_available_languages, get_available_models, get_current_model,
    transcribe_audio_file, transcribe_base64_audio, clear_model_cache,
    setup_dolphin_model, get_model_cache_size
)

router = APIRouter(prefix="/api/asr")

def cleanup_temp_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except OSError:
        pass

@router.get(
    "/languages",
    response_model=LanguagesResponse,
    tags=["Languages"],
    summary="Get available languages"
)
async def get_languages():
    try:
        languages = get_available_languages()
        return LanguagesResponse(success=True, languages=languages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get languages: {str(e)}"
        )

@router.get(
    "/models",
    response_model=ModelsResponse,
    tags=["Models"],
    summary="Get available models"
)
async def get_models():
    try:
        return ModelsResponse(
            success=True,
            models=get_available_models(),
            current_model=get_current_model(),
            cache_size=get_model_cache_size()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get models: {str(e)}"
        )

@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    tags=["Transcription"],
    summary="Transcribe audio file"
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = Form(None, description="Language code (e.g., 'en')"),
    region: str = Form(None, description="Region code (e.g., 'us')"),
    model: str = Form("small", description="ASR model to use")
):
    if not audio.content_type or not audio.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file"
        )
    
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            content = await audio.read()
            temp_file.write(content)
        
        if not setup_dolphin_model(model):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load ASR model: {model}"
            )
        
        result = transcribe_audio_file(temp_file_path, language, region)
        return TranscribeResponse(**result, success=True, used_model=model)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
    finally:
        if temp_file_path:
            cleanup_temp_file(temp_file_path)

@router.post(
    "/transcribe/base64",
    response_model=TranscribeResponse,
    tags=["Transcription"],
    summary="Transcribe base64 audio"
)
async def transcribe_base64(request: ASRRequest):
    try:
        if not setup_dolphin_model(request.model):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load ASR model: {request.model}"
            )
        
        result = transcribe_base64_audio(
            request.audio_data, request.language, request.region
        )
        return TranscribeResponse(**result, success=True, used_model=request.model)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )

@router.delete(
    "/cache",
    response_model=GeneralResponse,
    tags=["Health & Management"],
    summary="Clear model cache"
)
async def clear_cache():
    try:
        cached_count = clear_model_cache()
        return GeneralResponse(
            success=True,
            message=f"ASR model cache cleared. Removed {cached_count} cached models."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.get(
    "/health",
    response_class=PlainTextResponse,
    tags=["Health & Management"],
    summary="Health check"
)
async def health_check():
    return PlainTextResponse("healthy")
