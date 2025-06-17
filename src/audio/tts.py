import os
import tempfile
import wave
import traceback
from typing import Optional
from src.audio.core.piper import load_model
from src.config.tts_settings import (
    PIPER_VOICES, current_piper_voice, current_piper_speaker,
    current_piper_speed, current_piper_noise_scale, current_piper_noise_scale_w,
    get_voice_speaker_count
)


def create_speech_audio(text: str, voice_key: Optional[str] = None) -> Optional[str]:
    if not text or not text.strip():
        return None

    voice_to_use = voice_key or current_piper_voice

    if not voice_to_use:
        print("No voice specified and no default voice available")
        return None

    model = load_model(voice_to_use)
    if not model:
        print(f"Failed to load voice {voice_to_use}")
        return None

    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.close()

        max_speakers = get_voice_speaker_count(voice_to_use)
        speaker_id = min(current_piper_speaker, max_speakers -
                         1) if max_speakers > 1 else None

        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(model.config.sample_rate)

            print(f"Synthesizing: {text[:50]}...")

            try:
                synthesis_kwargs = {
                    'length_scale': 1.0 / current_piper_speed,
                    'noise_scale': current_piper_noise_scale,
                    'noise_w': current_piper_noise_scale_w
                }

                if speaker_id is not None:
                    synthesis_kwargs['speaker_id'] = speaker_id

                model.synthesize(text, wav_file, **synthesis_kwargs)

            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    print(
                        f"Basic synthesize method doesn't support synthesis parameters: {e}")
                    print("Falling back to basic synthesis without parameters")
                    model.synthesize(text, wav_file)
                else:
                    raise e

        print(f"Audio synthesized and saved to: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        print(f"Error synthesizing speech: {e}")
        traceback.print_exc()
        try:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        except:
            pass
        return None


def get_voice_info(voice_key: str) -> dict:
    return PIPER_VOICES.get(voice_key, {})


def change_voice_settings(voice: Optional[str] = None,
                          speaker: Optional[int] = None,
                          speed: Optional[float] = None,
                          noise_scale: Optional[float] = None,
                          noise_scale_w: Optional[float] = None) -> dict:
    global current_piper_voice, current_piper_speaker, current_piper_speed
    global current_piper_noise_scale, current_piper_noise_scale_w

    if voice is not None and voice in PIPER_VOICES:
        current_piper_voice = voice

    if speaker is not None:
        max_speakers = get_voice_speaker_count(
            current_piper_voice) if current_piper_voice else 1
        current_piper_speaker = max(0, min(int(speaker), max_speakers - 1))

    if speed is not None:
        current_piper_speed = max(0.1, min(3.0, float(speed)))

    if noise_scale is not None:
        current_piper_noise_scale = max(0.0, min(1.0, float(noise_scale)))

    if noise_scale_w is not None:
        current_piper_noise_scale_w = max(0.0, min(1.0, float(noise_scale_w)))

    return {
        "voice": current_piper_voice,
        "speaker": current_piper_speaker,
        "speed": current_piper_speed,
        "noise_scale": current_piper_noise_scale,
        "noise_w": current_piper_noise_scale_w
    }


def get_current_voice_settings() -> dict:
    return {
        "voice": current_piper_voice,
        "speaker": current_piper_speaker,
        "speed": current_piper_speed,
        "noise_scale": current_piper_noise_scale,
        "noise_w": current_piper_noise_scale_w
    }


def validate_voice_exists(voice_key: str) -> bool:
    return voice_key in PIPER_VOICES
