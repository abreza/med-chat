import os
import dolphin
from .utils import convert_audio_to_wav_file
from .core.dolphin import setup_dolphin_model, get_dolphin_model
from src.config.asr_settings import current_language, current_region


def transcribe(audio_tuple, language=None, region=None):
    dolphin_model = get_dolphin_model()

    if audio_tuple is None:
        return ""

    try:
        if isinstance(audio_tuple, tuple):
            sample_rate, audio_data = audio_tuple
        else:
            audio_data = audio_tuple
            sample_rate = 16000

        if audio_data is None or len(audio_data) == 0:
            return ""

        wav_file_path = convert_audio_to_wav_file(audio_data, sample_rate)
        if wav_file_path is None:
            return ""

        if not setup_dolphin_model():
            return "Error: Could not load Dolphin ASR model"

        waveform = dolphin.load_audio(wav_file_path)

        kwargs = {
            "predict_time": False,
            "padding_speech": False
        }

        lang_to_use = language if language is not None else current_language
        region_to_use = region if region is not None else current_region

        if lang_to_use:
            kwargs["lang_sym"] = lang_to_use
            if region_to_use:
                kwargs["region_sym"] = region_to_use

        result = dolphin_model(waveform, **kwargs)

        try:
            os.unlink(wav_file_path)
        except:
            pass

        transcription = result.text.strip()
        detected_info = f"Language: {result.language}"
        if hasattr(result, 'region') and result.region:
            detected_info += f", Region: {result.region}"

        print(f"Transcribed: {transcription} ({detected_info})")

        return transcription

    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
