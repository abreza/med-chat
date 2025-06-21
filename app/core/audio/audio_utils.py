import numpy as np
import wave
import tempfile
from typing import Optional, Tuple


def create_temp_wav_file() -> str:
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_file.close()
    return temp_file.name


def convert_audio_to_wav_file(audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
    if audio_data is None or len(audio_data) == 0:
        return None

    if audio_data.dtype != np.int16:
        if audio_data.dtype in [np.float32, np.float64]:
            audio_data = (audio_data * 32767).astype(np.int16)
        else:
            audio_data = audio_data.astype(np.int16)

    temp_file_path = create_temp_wav_file()

    try:
        with wave.open(temp_file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        return temp_file_path
    except Exception as e:
        print(f"Error converting audio to WAV: {e}")
        return None


def combine_audio_chunks(audio: Optional[Tuple], new_chunk: Optional[Tuple]) -> Optional[Tuple]:
    if new_chunk is None:
        return audio

    if audio is None:
        return new_chunk

    sample_rate, existing_audio = audio
    _, new_audio = new_chunk
    combined_audio = np.concatenate([existing_audio, new_audio])
    return (sample_rate, combined_audio)


def should_process_audio(audio: Optional[Tuple], min_duration_seconds: int = 2) -> bool:
    if audio is None:
        return False

    sample_rate, audio_data = audio
    return len(audio_data) > sample_rate * min_duration_seconds
