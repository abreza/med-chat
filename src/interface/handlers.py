import gradio as gr
from src.voice_chat import VoiceChatState
from src.llm import generate_ai_response, get_available_models, set_model
from src.audio.tts import (
    create_speech_audio, change_voice_settings, get_current_voice_settings,
    get_voice_info, validate_voice_exists
)
from src.config.asr_settings import language_to_regions
import src.config.asr_settings as asr_config
from src.config.tts_settings import (
    piper_voice_options, PIPER_VOICES, get_voice_speaker_count,
    get_voice_speaker_names, filter_voices_by_language
)


def update_regions(language):
    if not language:
        return [], None, False

    if language in language_to_regions:
        regions = language_to_regions[language]
        regions.sort(key=lambda x: x[0])
        default_value = regions[0][1] if regions else None
        return regions, default_value, True
    return [], None, False


def update_speaker_options(voice_key):
    if not voice_key or voice_key not in PIPER_VOICES:
        return gr.update(maximum=0, value=0, visible=False), ""

    speaker_count = get_voice_speaker_count(voice_key)
    speaker_names = get_voice_speaker_names(voice_key)

    if speaker_count > 1:
        if speaker_names:
            info_text = f"Speakers: {', '.join(speaker_names)}"
        else:
            info_text = f"{speaker_count} speakers available (0-{speaker_count-1})"

        return gr.update(
            maximum=speaker_count-1,
            value=0,
            visible=True,
            info=info_text
        ), info_text
    else:
        return gr.update(maximum=0, value=0, visible=False), "Single speaker voice"


def filter_voices_by_selected_language(language_filter):
    if not language_filter or language_filter == "All Languages":
        return piper_voice_options

    filtered_voices = filter_voices_by_language(language_filter)
    return filtered_voices


def send_message(message_data, state: VoiceChatState):
    if message_data is None:
        return state.get_conversation_display(), state, None, {"text": "", "files": []}
    
    message_text = message_data.get("text", "").strip()
    message_files = message_data.get("files", [])
    
    if not message_text:
        return state.get_conversation_display(), state, None, {"text": "", "files": []}

    state.add_message("user", message_text)

    messages = state.get_messages_for_api()
    ai_response = generate_ai_response(messages)

    state.add_message("assistant", ai_response)

    audio_file = create_speech_audio(ai_response)

    return state.get_conversation_display(), state, audio_file, {"text": "", "files": []}


def reset_conversation(state: VoiceChatState):
    state.clear_conversation()
    return [], state, None


def change_llm_model(model_name):
    success = set_model(model_name)
    if success:
        return f"LLM Model changed to: {model_name}"
    else:
        return f"Failed to change model to: {model_name}"


def update_language_settings(language, region):
    asr_config.current_language = language
    asr_config.current_region = region

    lang_info = "Auto-detect" if not language else language
    region_info = f" ({region})" if region else ""
    status = f"Language set to: {lang_info}{region_info}"

    return status


def update_tts_voice(voice_key):
    if validate_voice_exists(voice_key):
        settings = change_voice_settings(voice=voice_key)
        voice_info = get_voice_info(voice_key)
        status = f"TTS Voice changed to: {voice_info.get('name', voice_key)}"
        return status
    else:
        return f"Invalid voice: {voice_key}"


def update_tts_settings(voice_key, speaker_id, speed, noise_scale, noise_scale_w):
    if not validate_voice_exists(voice_key):
        return f"Invalid voice: {voice_key}"

    settings = change_voice_settings(
        voice=voice_key,
        speaker=speaker_id,
        speed=speed,
        noise_scale=noise_scale,
        noise_scale_w=noise_scale_w
    )

    voice_info = get_voice_info(voice_key)
    status = f"TTS Settings updated - Voice: {voice_info.get('name', voice_key)}, Speed: {speed:.1f}x"
    return status


def test_tts_voice(voice_key, speaker_id, speed, noise_scale, noise_scale_w):
    if not validate_voice_exists(voice_key):
        return None

    original_settings = get_current_voice_settings()
    change_voice_settings(
        voice=voice_key,
        speaker=speaker_id,
        speed=speed,
        noise_scale=noise_scale,
        noise_scale_w=noise_scale_w
    )

    test_text = f"سلام من یک موتور سخن‌گو پارسی هستم.."
    audio_file = create_speech_audio(test_text)

    change_voice_settings(**original_settings)

    return audio_file
