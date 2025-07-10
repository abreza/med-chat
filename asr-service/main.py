import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, APIRouter
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager

from config import ASR_CONFIG, FASTAPI_CONFIG, TAGS_METADATA, SERVER_CONFIG
from models import (
    ASRRequest, TranscribeResponse, LanguagesResponse, 
    ModelsResponse, ErrorResponse
)
from core import setup_dolphin_model, clear_model_cache
import routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting ASR Microservice...")
    
    ASR_CONFIG["model_dir"].mkdir(parents=True, exist_ok=True)
    ASR_CONFIG["assets_dir"].mkdir(parents=True, exist_ok=True)
    
    default_model = ASR_CONFIG["default_model"]
    print(f"Loading default ASR model: {default_model}")
    
    if setup_dolphin_model(default_model):
        print("✅ ASR Microservice ready!")
    else:
        print("⚠️ ASR Microservice started but default model failed to load")
    
    yield
    
    print("🔄 Shutting down ASR Microservice...")
    clear_model_cache()
    print("✅ ASR Microservice shutdown complete!")


app = FastAPI(
    title=FASTAPI_CONFIG["title"],
    version=FASTAPI_CONFIG["version"],
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    contact=FASTAPI_CONFIG["contact"],
    license_info=FASTAPI_CONFIG["license_info"],
    openapi_url="/api/asr/openapi.json",
    docs_url="/api/asr/docs",
)

router = APIRouter(prefix="/api/asr")


@router.get(
    "/languages",
    response_model=LanguagesResponse,
    tags=["Languages"],
    summary="Get available languages",
    description="Returns a list of all available languages and regions for ASR."
)
async def get_languages():
    return await routes.get_languages()


@router.get(
    "/models", 
    response_model=ModelsResponse,
    tags=["Models"],
    summary="Get available models",
    description="Returns information about available ASR models and cache status."
)
async def get_models():
    return await routes.get_models()


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    tags=["Transcription"],
    summary="Transcribe audio file",
    description="Upload an audio file for transcription.",
    responses={
        200: {"model": TranscribeResponse, "description": "Transcription successful"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Transcription failed"}
    }
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = Form(None, description="Language code (optional)"),
    region: str = Form(None, description="Region code (optional)"),
    model: str = Form("small", description="ASR model to use")
):
    return await routes.transcribe_audio(audio, language, region, model)


@router.post(
    "/transcribe/base64",
    response_model=TranscribeResponse, 
    tags=["Transcription"],
    summary="Transcribe base64 audio",
    description="Transcribe base64 encoded audio data.",
    responses={
        200: {"model": TranscribeResponse, "description": "Transcription successful"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Transcription failed"}
    }
)
async def transcribe_base64(request: ASRRequest):
    return await routes.transcribe_base64(request)


@router.delete(
    "/cache",
    tags=["Health & Management"],
    summary="Clear model cache",
    description="Clear all cached ASR models to free up memory. Models will be reloaded on next use."
)
async def clear_cache():
    return await routes.clear_cache()


@router.get(
    "/health",
    response_class=PlainTextResponse,
    tags=["Health & Management"],
    summary="Health check", 
    description="Simple health check that returns 'healthy' string."
)
async def health_check():
    return await routes.health_check()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=SERVER_CONFIG["reload"]
    )
