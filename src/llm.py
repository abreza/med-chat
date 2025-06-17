from openai import OpenAI
from src.config.base_settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    APP_NAME,
    APP_URL
)

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


def generate_ai_response(messages):
    try:
        system_message = {
            "role": "system",
            "content": """You are an intelligent medical AI assistant specializing in Persian language healthcare support. Your responsibilities include:

- Providing general medical information and answering health-related questions
- Helping users understand symptoms and medical conditions
- Offering guidance on first aid and preventive care
- Providing general recommendations for healthy lifestyle choices

Response Guidelines:
- Keep responses concise and easily understandable
- Respond in fluent and simple Persian language
- Avoid creating unnecessary alarm and respond with compassion and care
- Maintain a helpful and supportive tone throughout conversations"""
        }

        formatted_messages = [system_message] + messages

        extra_headers = {}
        if APP_URL:
            extra_headers["HTTP-Referer"] = APP_URL
        if APP_NAME:
            extra_headers["X-Title"] = APP_NAME

        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=formatted_messages,
            extra_headers=extra_headers if extra_headers else None
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenRouter API error: {e}")
        if "insufficient_quota" in str(e).lower():
            return "عذر می‌خواهم، در حال حاضر امکان پاسخ‌گویی وجود ندارد. لطفا بعدا دوباره تلاش کنید."
        elif "rate_limit" in str(e).lower():
            return "به دلیل محدودیت نرخ درخواست، لطفا کمی صبر کنید و دوباره تلاش کنید."
        else:
            return "خطایی در سیستم رخ داده است. لطفا دوباره تلاش کنید."


def get_available_models():
    try:
        return [
            "qwen/qwen3-14b",
            "microsoft/phi-4",
            "openai/gpt-4.1-nano",
            "openai/gpt-4.1-mini",
            "anthropic/claude-4-sonnet",
            "anthropic/claude-4-opus",
            "openai/gpt-4.1",
            "google/gemini-2.5-pro",
            "anthropic/claude-3.7-sonnet",
            "google/gemini-2.0-flash",
            "meta-llama/llama-4-scout",
            "meta-llama/llama-4-maverick",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.5-flash",
            "anthropic/claude-3.5-haiku",
            "google/gemini-2.0-flash-lite",
            "deepseek/deepseek-r1",
            "meta-llama/llama-3.3-70b-instruct",
            "mistralai/mistral-large-2407",
            "cohere/command-r-plus",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "google/gemma-2-27b-it",
            "meta-llama/llama-3.2-11b-vision-instruct",
            "mistralai/mistral-7b-instruct",
        ]
    except Exception as e:
        print(f"Error fetching available models: {e}")
        return [OPENROUTER_MODEL]


def set_model(model_name):
    global OPENROUTER_MODEL
    if model_name in get_available_models():
        OPENROUTER_MODEL = model_name
        return True
    return False
