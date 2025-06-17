import numpy as np
import wave
import tempfile


def convert_audio_to_wav_file(audio_data, sample_rate=16000):
    if audio_data is None or len(audio_data) == 0:
        return None

    if audio_data.dtype != np.int16:
        if audio_data.dtype in [np.float32, np.float64]:
            audio_data = (audio_data * 32767).astype(np.int16)
        else:
            audio_data = audio_data.astype(np.int16)

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

    with wave.open(temp_file.name, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    temp_file.close()
    return temp_file.name


def combine_audio_chunks(audio, new_chunk):
    if new_chunk is None:
        return audio

    if audio is None:
        return new_chunk

    sample_rate, existing_audio = audio
    _, new_audio = new_chunk
    combined_audio = np.concatenate([existing_audio, new_audio])
    return (sample_rate, combined_audio)


def should_process_audio(audio, min_duration_seconds=2):
    if audio is None:
        return False

    sample_rate, audio_data = audio
    return len(audio_data) > sample_rate * min_duration_seconds
