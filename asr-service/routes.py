import os
import tempfile
from fastapi import HTTPException, status, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from models import ASRRequest, TranscribeResponse, LanguagesResponse, ModelsResponse
from core import (
    get_available_languages, get_available_models, get_current_model,
    transcribe_audio_file, transcribe_base64_audio, clear_model_cache,
    setup_dolphin_model, get_model_cache_size
)


def cleanup_temp_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except OSError:
        pass


async def get_languages():
    try:
        languages = get_available_languages()
        return LanguagesResponse(
            success=True,
            languages=languages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get languages: {str(e)}"
        )


async def get_models():
    try:
        models = get_available_models()
        current_model = get_current_model()
        cache_size = get_model_cache_size()

        return ModelsResponse(
            success=True,
            models=models,
            current_model=current_model,
            cache_size=cache_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get models: {str(e)}"
        )


async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form(None),
    region: str = Form(None),
    model: str = Form("small")
):
    try:
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        try:
            content = await audio.read()
            temp_file.write(content)
            temp_file.close()

            if not setup_dolphin_model(model):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to load ASR model: {model}"
                )

            result = transcribe_audio_file(temp_file.name, language, region)

            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Transcription failed"
                )

            return TranscribeResponse(
                success=True,
                text=result.get('text', ''),
                language=result.get('language'),
                region=result.get('region'),
                confidence=result.get('confidence'),
                model_used=model
            )

        finally:
            cleanup_temp_file(temp_file.name)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


async def transcribe_base64(request: ASRRequest):
    try:
        if not request.audio_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="audio_data is required"
            )

        if not setup_dolphin_model(request.model):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load ASR model: {request.model}"
            )

        result = transcribe_base64_audio(
            request.audio_data,
            request.language,
            request.region
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transcription failed"
            )

        return TranscribeResponse(
            success=True,
            text=result.get('text', ''),
            language=result.get('language'),
            region=result.get('region'),
            confidence=result.get('confidence'),
            model_used=request.model
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


async def clear_cache():
    try:
        cached_count = clear_model_cache()
        return {
            "success": True,
            "message": f"ASR model cache cleared. Removed {cached_count} cached models."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


async def health_check():
    return PlainTextResponse("healthy")
