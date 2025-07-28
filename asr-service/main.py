import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from config import ASR_CONFIG, FASTAPI_CONFIG, TAGS_METADATA, SERVER_CONFIG
from core import setup_dolphin_model, clear_model_cache
from routes import router

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

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=SERVER_CONFIG["reload"]
    )
