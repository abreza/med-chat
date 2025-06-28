import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from contextlib import asynccontextmanager

from config import TTS_CONFIG, FASTAPI_CONFIG, TAGS_METADATA, SERVER_CONFIG
from models import VoicesResponse, TTSResponse, ErrorResponse, TTSRequest
from core import load_voices_config, clear_model_cache
import routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting TTS Microservice...")

    TTS_CONFIG["model_dir"].mkdir(parents=True, exist_ok=True)

    load_voices_config()

    print("✅ TTS Microservice ready!")
    yield

    print("🔄 Shutting down TTS Microservice...")
    clear_model_cache()
    print("✅ TTS Microservice shutdown complete!")


app = FastAPI(
    title=FASTAPI_CONFIG["title"],
    version=FASTAPI_CONFIG["version"],
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    contact=FASTAPI_CONFIG["contact"],
    license_info=FASTAPI_CONFIG["license_info"],
    root_path="/api/tts"
)


@app.get(
    "/voices",
    response_model=VoicesResponse,
    tags=["Voices"],
    summary="Get available voices",
    description="Returns a list of all available voices with their properties including language, quality, and speaker information."
)
async def get_voices():
    return await routes.get_voices()


@app.post(
    "/synthesize",
    response_class=FileResponse,
    tags=["Speech Synthesis"],
    summary="Convert text to speech",
    responses={
        200: {
            "description": "Audio file generated successfully",
            "content": {"audio/wav": {}},
            "headers": {
                "X-Audio-Duration": {"description": "Audio duration in seconds"},
                "X-Voice-Key": {"description": "Voice used for synthesis"},
                "X-Speaker-ID": {"description": "Speaker ID used"},
                "X-Speed": {"description": "Speed multiplier used"}
            }
        },
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Speech synthesis failed"}
    }
)
async def synthesize_speech(request: TTSRequest):
    return await routes.synthesize_speech(request)


@app.delete(
    "/cache",
    response_model=TTSResponse,
    tags=["Health & Management"],
    summary="Clear model cache",
    description="Clear all cached voice models to free up memory. Models will be reloaded on next use."
)
async def clear_cache():
    return await routes.clear_cache()


@app.get(
    "/health",
    response_class=PlainTextResponse,
    tags=["Health & Management"],
    summary="Health check",
    description="Simple health check that returns 'healthy' string."
)
async def health_check():
    return await routes.health_check()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=SERVER_CONFIG["reload"]
    )
