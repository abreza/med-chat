from typing import Optional
import tempfile
import os


def create_temp_audio_file(suffix: str = ".wav") -> str:
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_file.close()
    return temp_file.name


def configure_wav_file(wav_file, sample_rate: int) -> None:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)


def cleanup_temp_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            return True
        return False
    except Exception:
        return False


def prepare_synthesis_kwargs(speaker_id: Optional[int], num_speakers: int, speed: float,
                             noise_scale: float, noise_scale_w: float) -> dict:
    synthesis_kwargs = {
        'length_scale': 1.0 / speed,
        'noise_scale': noise_scale,
        'noise_w': noise_scale_w
    }

    if speaker_id is not None and num_speakers > 1:
        speaker_id = max(0, min(speaker_id, num_speakers - 1))
        synthesis_kwargs['speaker_id'] = speaker_id

    return synthesis_kwargs
