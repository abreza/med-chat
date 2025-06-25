PIPER_VOICES_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"

AVAILABLE_MODELS = [
    "openai/gpt-4.1-nano", "openai/gpt-4.1-mini", "openai/gpt-4.1",
    "anthropic/claude-4-sonnet", "anthropic/claude-4-opus", "google/gemini-2.5-pro",
    "anthropic/claude-3.7-sonnet", "google/gemini-2.0-flash", "anthropic/claude-3.5-sonnet",
    "google/gemini-2.5-flash", "meta-llama/llama-3.2-11b-vision-instruct", "qwen/qwen3-14b",
    "microsoft/phi-4", "meta-llama/llama-4-scout", "meta-llama/llama-4-maverick",
    "anthropic/claude-3.5-haiku", "google/gemini-2.0-flash-lite", "deepseek/deepseek-r1",
    "meta-llama/llama-3.3-70b-instruct", "mistralai/mistral-large-2407", "cohere/command-r-plus",
    "nvidia/llama-3.1-nemotron-70b-instruct", "google/gemma-2-27b-it", "mistralai/mistral-7b-instruct",
]

VISION_MODELS = {
    "openai/gpt-4.1", "openai/gpt-4.1-nano", "openai/gpt-4.1-mini",
    "anthropic/claude-4-sonnet", "anthropic/claude-4-opus", "google/gemini-2.5-pro",
    "anthropic/claude-3.7-sonnet", "google/gemini-2.0-flash", "anthropic/claude-3.5-sonnet",
    "google/gemini-2.5-flash", "meta-llama/llama-3.2-11b-vision-instruct",
}

DEFAULT_TTS_SETTINGS = {"speaker": 0, "speed": 1.0,
                        "noise_scale": 0.667, "noise_scale_w": 0.8}

SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.webp']
