import os
import numpy as np
import wave
import tempfile
import logging
from typing import Union, Tuple, Optional

import dolphin
from .setup_dolphin import setup_dolphin_model, get_dolphin_model
from .config import current_language, current_region

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_audio_to_wav_file(audio_data: Union[np.ndarray, bytes], sample_rate: int = 16000) -> Optional[str]:
    if audio_data is None or (hasattr(audio_data, '__len__') and len(audio_data) == 0):
        return None

    try:
        if isinstance(audio_data, bytes):
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False)
            temp_file.write(audio_data)
            temp_file.close()
            return temp_file.name

        elif isinstance(audio_data, np.ndarray):
            if audio_data.dtype != np.int16:
                if audio_data.dtype in [np.float32, np.float64]:
                    audio_data = (audio_data * 32767).astype(np.int16)
                else:
                    audio_data = audio_data.astype(np.int16)

            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False)
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())

            temp_file.close()
            return temp_file.name

        else:
            logger.error(f"Unsupported audio data type: {type(audio_data)}")
            return None

    except Exception as e:
        logger.error(f"Error converting audio data: {e}")
        return None


def transcribe_file(file_path: str, language: Optional[str] = current_language, region: Optional[str] = current_region) -> str:
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        return ""

    try:
        if not setup_dolphin_model():
            logger.error("Failed to load Dolphin ASR model")
            return ""

        dolphin_model = get_dolphin_model()
        if dolphin_model is None:
            logger.error("Dolphin ASR model is not available")
            return ""

        waveform = dolphin.load_audio(file_path)

        kwargs = {
            "predict_time": False,
            "padding_speech": False,
            "lang_sym": language,
            "region_sym": region
        }

        result = dolphin_model(waveform, **kwargs)

        transcription = result.text.strip() if hasattr(result, 'text') else ""

        detected_info = f"Language: {getattr(result, 'language', 'unknown')}"
        if hasattr(result, 'region') and result.region:
            detected_info += f", Region: {result.region}"

        logger.info(f"Transcribed: '{transcription}' ({detected_info})")

        return transcription

    except Exception as e:
        logger.error(f"Transcription error for file {file_path}: {e}")
        return ""

    finally:
        try:
            if file_path.startswith(tempfile.gettempdir()):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(
                f"Failed to clean up temporary file {file_path}: {e}")


def transcribe(audio_input: Union[Tuple, np.ndarray, bytes, str],
               language: Optional[str] = current_language,
               region: Optional[str] = current_region) -> str:
    if audio_input is None:
        return ""

    try:
        if isinstance(audio_input, str):
            return transcribe_file(audio_input, language, region)

        elif isinstance(audio_input, tuple) and len(audio_input) == 2:
            sample_rate, audio_data = audio_input
            wav_file_path = convert_audio_to_wav_file(audio_data, sample_rate)

        elif isinstance(audio_input, (np.ndarray, bytes)):
            wav_file_path = convert_audio_to_wav_file(audio_input)

        else:
            logger.error(f"Unsupported audio input type: {type(audio_input)}")
            return ""

        if wav_file_path:
            return transcribe_file(wav_file_path, language, region)
        else:
            logger.error("Failed to convert audio input to WAV file")
            return ""

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""
