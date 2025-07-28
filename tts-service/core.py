import re
import json
import os
import tempfile
from typing import Optional, Tuple, Generator
from piper.voice import PiperVoice
from config import TTS_CONFIG

voices_config = {}
model_cache = {}


def load_voices_config():
    global voices_config

    try:
        if not TTS_CONFIG["voices_file"].exists():
            raise FileNotFoundError(
                f"Voices file not found: {TTS_CONFIG['voices_file']}")

        with open(TTS_CONFIG["voices_file"], 'r', encoding='utf-8') as f:
            voices_data = json.load(f)

        processed_voices = {}
        for voice_key, voice_info in voices_data.items():
            onnx_file = config_file = None

            for file_path in voice_info.get("files", {}):
                if file_path.endswith(".onnx"):
                    onnx_file = file_path
                elif file_path.endswith(".onnx.json"):
                    config_file = file_path

            if onnx_file and config_file:
                processed_voices[voice_key] = {
                    "name": voice_info.get("name", voice_key),
                    "language": voice_info.get("language", {}),
                    "quality": voice_info.get("quality", "unknown"),
                    "num_speakers": voice_info.get("num_speakers", 1),
                    "speaker_id_map": voice_info.get("speaker_id_map", {}),
                    "model_file": onnx_file,
                    "config_file": config_file,
                    "files": voice_info.get("files", {})
                }

        voices_config = processed_voices
        print(f"✅ Loaded {len(voices_config)} voices")

    except Exception as e:
        print(f"❌ Error loading voices config: {e}")
        voices_config = {}


def get_voice_file_paths(voice_key: str) -> Tuple[Optional[str], Optional[str]]:
    if voice_key not in voices_config:
        return None, None

    voice_info = voices_config[voice_key]
    model_path = TTS_CONFIG["model_dir"] / voice_info["model_file"]
    config_path = TTS_CONFIG["model_dir"] / voice_info["config_file"]

    return model_path, config_path


def load_voice_model(voice_key: str):
    global model_cache

    if voice_key in model_cache:
        return model_cache[voice_key]

    temp_config_path = None
    try:
        model_path, config_path = get_voice_file_paths(voice_key)

        if not model_path or not config_path:
            raise ValueError(f"Voice {voice_key} not found in configuration")

        if not model_path.exists() or not config_path.exists():
            raise FileNotFoundError(
                f"Voice files not found: {model_path}, {config_path}")

        final_config_path = str(config_path)
        ezafe_model_path = TTS_CONFIG.get("ezafe_model_path")

        if ezafe_model_path and os.path.exists(ezafe_model_path):
            print(f"ℹ️ Ezafe model found at '{ezafe_model_path}', updating config...")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config_data['ezafe_model_path'] = ezafe_model_path

            with tempfile.NamedTemporaryFile(
                mode='w', delete=False, suffix=".json", encoding='utf-8', dir="/tmp"
            ) as temp_f:
                json.dump(config_data, temp_f)
                temp_config_path = temp_f.name
            
            final_config_path = temp_config_path
            print(f"📝 Using temporary config: {final_config_path}")

        use_cuda = TTS_CONFIG.get("use_cuda", False)
        print(f"ℹ️ CUDA usage set to: {use_cuda}")
        
        model = PiperVoice.load(
            model_path=str(model_path), 
            config_path=final_config_path, 
            use_cuda=use_cuda
        )
        model_cache[voice_key] = model

        print(f"✅ Loaded voice model: {voice_key}")
        return model

    except Exception as e:
        print(f"❌ Error loading voice model {voice_key}: {e}")
        return None
    finally:
        if temp_config_path and os.path.exists(temp_config_path):
            os.unlink(temp_config_path)
            print(f"🗑️ Removed temporary config file: {temp_config_path}")


def configure_wav_file(wav_file, sample_rate: int):
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)


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


def clear_model_cache() -> int:
    global model_cache
    cached_count = len(model_cache)
    model_cache.clear()
    return cached_count


def get_voices_config() -> dict:
    return voices_config


def get_model_cache_size() -> int:
    return len(model_cache)


def synthesize_stream_audio(model: PiperVoice, text: str, **synthesis_kwargs) -> Generator[bytes, None, None]:
    try:
        processed_text = re.sub(r'\n', ' ', text)
        processed_text = re.sub(r'[?.:;!!؟]|\.{3}', '،', processed_text)
        
        for audio_chunk in model.synthesize_stream_raw(processed_text, **synthesis_kwargs):
            yield audio_chunk
            
    except Exception as e:
        print(f"❌ Error in streaming synthesis: {e}")
        raise


def add_wav_header(sample_rate: int, num_channels: int = 1, bits_per_sample: int = 16) -> bytes:
    data_size = 0xFFFFFFFF - 36
    
    header = bytearray(44)
    
    header[0:4] = b'RIFF'
    header[4:8] = (data_size + 36).to_bytes(4, 'little')
    header[8:12] = b'WAVE'
    
    header[12:16] = b'fmt '
    header[16:20] = (16).to_bytes(4, 'little')
    header[20:22] = (1).to_bytes(2, 'little')
    header[22:24] = num_channels.to_bytes(2, 'little')
    header[24:28] = sample_rate.to_bytes(4, 'little')
    
    bytes_per_second = sample_rate * num_channels * (bits_per_sample // 8)
    header[28:32] = bytes_per_second.to_bytes(4, 'little')
    
    block_align = num_channels * (bits_per_sample // 8)
    header[32:34] = block_align.to_bytes(2, 'little')
    header[34:36] = bits_per_sample.to_bytes(2, 'little')
    
    header[36:40] = b'data'
    header[40:44] = data_size.to_bytes(4, 'little')
    
    return bytes(header)