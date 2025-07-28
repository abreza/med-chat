import os
import tempfile
import wave
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.background import BackgroundTask
from models import TTSRequest, TTSResponse, VoicesResponse
from core import (
    get_voices_config, load_voice_model,
    configure_wav_file, prepare_synthesis_kwargs, clear_model_cache
)

router = APIRouter(prefix="/api/tts")


def cleanup_temp_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except OSError:
        pass


@router.get(
    "/voices",
    response_model=VoicesResponse,
    tags=["Voices"],
    summary="Get available voices",
    description="Returns a list of all available voices."
)
async def get_voices():
    voices_config = get_voices_config()
    return {
        "success": True,
        "voices": {
            voice_key: {
                "name": voice_info["name"],
                "language": voice_info["language"],
                "quality": voice_info["quality"],
                "num_speakers": voice_info["num_speakers"],
                "speaker_names": list(voice_info["speaker_id_map"].keys()) if voice_info.get("speaker_id_map") else []
            }
            for voice_key, voice_info in voices_config.items()
        }
    }


@router.post(
    "/synthesize",
    response_class=FileResponse,
    tags=["Speech Synthesis"],
    summary="Convert text to speech",
    responses={
        200: {
            "description": "Audio file generated successfully",
            "content": {"audio/wav": {}},
            "headers": {
                "X-Audio-Duration": {"description": "Duration of the audio in seconds"},
                "X-Voice-Key": {"description": "Voice used for synthesis"},
            },
        }
    }
)
async def synthesize_speech(request: TTSRequest):
    try:
        voices_config = get_voices_config()

        if request.voice_key not in voices_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Voice '{request.voice_key}' not found. Available voices: {list(voices_config.keys())}"
            )

        model = load_voice_model(request.voice_key)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load voice model: {request.voice_key}"
            )

        voice_info = voices_config[request.voice_key]
        num_speakers = voice_info["num_speakers"]

        if request.speaker_id >= num_speakers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Speaker ID {request.speaker_id} not available. Voice has {num_speakers} speakers (0-{num_speakers-1})"
            )

        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file_path = temp_file.name
        temp_file.close()

        try:
            with wave.open(temp_file_path, 'wb') as wav_file:
                configure_wav_file(wav_file, model.config.sample_rate)

                synthesis_kwargs = prepare_synthesis_kwargs(
                    request.speaker_id, num_speakers, request.speed,
                    request.noise_scale, request.noise_scale_w
                )

                model.synthesize(request.text, wav_file, **synthesis_kwargs)

            with wave.open(temp_file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate) if sample_rate != 0 else 0

            return FileResponse(
                temp_file_path,
                media_type="audio/wav",
                filename=f"tts_output_{request.voice_key}.wav",
                headers={
                    "X-Audio-Duration": str(duration),
                    "X-Voice-Key": request.voice_key,
                },
                background=BackgroundTask(cleanup_temp_file, temp_file_path)
            )

        except Exception as e:
            cleanup_temp_file(temp_file_path)
            raise e

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.delete(
    "/cache",
    response_model=TTSResponse,
    tags=["Health & Management"],
    summary="Clear model cache",
    description="Clears all cached voice models from memory to free up resources."
)
async def clear_cache():
    cached_count = clear_model_cache()
    return {
        "success": True,
        "message": f"Model cache cleared. Removed {cached_count} cached models."
    }


@router.get(
    "/health",
    response_class=PlainTextResponse,
    tags=["Health & Management"],
    summary="Health check",
    description="Simple health check that returns a 'healthy' string."
)
async def health_check():
    return PlainTextResponse("healthy")
