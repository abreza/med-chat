import os
import urllib.request
import wave
import tempfile
import traceback
from typing import Optional, Dict, Any, Tuple
from pathlib import Path


class PiperEngine:
    def __init__(self, model_dir: Path, voices_config: Dict[str, Any]):
        self.model_dir = model_dir
        self.voices_config = voices_config
        self._model_cache: Dict[str, Any] = {}

    def get_voice_file_paths(self, voice_key: str) -> Tuple[Optional[Path], Optional[Path]]:
        if voice_key not in self.voices_config:
            return None, None

        voice_info = self.voices_config[voice_key]
        model_path = None
        config_path = None

        for file_path, file_info in voice_info.get("files", {}).items():
            if file_path.endswith(".onnx"):
                model_path = self.model_dir / file_path
            elif file_path.endswith(".onnx.json"):
                config_path = self.model_dir / file_path

        return model_path, config_path

    def download_voice_files(self, voice_key: str) -> bool:
        if voice_key not in self.voices_config:
            print(f"Unknown voice: {voice_key}")
            return False

        voice_info = self.voices_config[voice_key]
        model_path, config_path = self.get_voice_file_paths(voice_key)

        if not model_path or not config_path:
            print(f"Could not determine file paths for voice: {voice_key}")
            return False

        model_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if not model_path.exists():
            try:
                print(f"Downloading Piper voice model: {voice_key}")
                print(f"URL: {voice_info['model_url']}")
                urllib.request.urlretrieve(voice_info["model_url"], model_path)
                print(f"Downloaded {model_path}")
            except Exception as e:
                print(f"Error downloading model {voice_key}: {e}")
                return False

        if not config_path.exists():
            try:
                print(f"Downloading Piper voice config: {voice_key}")
                print(f"URL: {voice_info['config_url']}")
                urllib.request.urlretrieve(voice_info["config_url"], config_path)
                print(f"Downloaded {config_path}")
            except Exception as e:
                print(f"Error downloading config {voice_key}: {e}")
                return False

        return True

    def load_voice_model(self, voice_key: str) -> Optional[Any]:
        if voice_key in self._model_cache:
            print(f"Using cached model for voice: {voice_key}")
            return self._model_cache[voice_key]

        try:
            from piper.voice import PiperVoice

            model_path, config_path = self.get_voice_file_paths(voice_key)

            if not model_path:
                print(f"Could not determine model path for voice: {voice_key}")
                return None

            if not model_path.exists():
                print(f"Model file not found locally: {model_path}")
                if not self.download_voice_files(voice_key):
                    return None

            print(f"Loading Piper voice: {voice_key}")
            print(f"Model path: {model_path}")
            model = PiperVoice.load(str(model_path))

            self._model_cache[voice_key] = model
            print(f"Successfully loaded and cached Piper voice: {voice_key}")
            
            return model

        except ImportError:
            print("Piper TTS not installed. Install with: pip install piper-tts")
            return None
        except Exception as e:
            print(f"Error loading Piper voice {voice_key}: {e}")
            return None

    def synthesize_speech(self, text: str, voice_key: str, 
                         speaker_id: Optional[int] = None,
                         speed: float = 1.0,
                         noise_scale: float = 0.667,
                         noise_scale_w: float = 0.8) -> Optional[str]:
        if not text or not text.strip():
            return None

        model = self.load_voice_model(voice_key)
        if not model:
            print(f"Failed to load voice {voice_key}")
            return None

        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.close()
            temp_file_path = temp_file.name
            
            with wave.open(temp_file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(model.config.sample_rate)

                voice_info = self.voices_config.get(voice_key, {})
                num_speakers = voice_info.get("num_speakers", 1)
                supports_speakers = num_speakers > 1

                synthesis_kwargs = {
                    'length_scale': 1.0 / speed,
                    'noise_scale': noise_scale,
                    'noise_w': noise_scale_w
                }

                if speaker_id is not None and supports_speakers:
                    speaker_id = max(0, min(speaker_id, num_speakers - 1))
                    synthesis_kwargs['speaker_id'] = speaker_id

                model.synthesize(text, wav_file, **synthesis_kwargs)

            print(f"Audio synthesized and saved to: {temp_file_path}")
            return temp_file_path

        except Exception as e:
            print(f"Error synthesizing speech: {e}")
            traceback.print_exc()
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            return None
