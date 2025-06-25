import wave
import urllib.request
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from .utils import create_temp_audio_file, configure_wav_file, cleanup_temp_file, prepare_synthesis_kwargs


class PiperEngine:
    def __init__(self, model_dir: Path, voices_config: Dict[str, Any]):
        self.model_dir = model_dir
        self.voices_config = voices_config
        self._model_cache: Dict[str, Any] = {}

    def get_voice_file_paths(self, voice_key: str) -> Tuple[Optional[Path], Optional[Path]]:
        if voice_key not in self.voices_config:
            return None, None
        voice_info = self.voices_config[voice_key]
        model_path = config_path = None
        for file_path in voice_info.get("files", {}):
            if file_path.endswith(".onnx"):
                model_path = self.model_dir / file_path
            elif file_path.endswith(".onnx.json"):
                config_path = self.model_dir / file_path
        return model_path, config_path

    def download_voice_files(self, voice_key: str) -> bool:
        if voice_key not in self.voices_config:
            return False
        voice_info = self.voices_config[voice_key]
        model_path, config_path = self.get_voice_file_paths(voice_key)
        if not model_path or not config_path:
            return False

        model_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if not model_path.exists():
                urllib.request.urlretrieve(voice_info["model_url"], model_path)
            if not config_path.exists():
                urllib.request.urlretrieve(
                    voice_info["config_url"], config_path)
            return True
        except Exception:
            return False

    def load_voice_model(self, voice_key: str) -> Optional[Any]:
        if voice_key in self._model_cache:
            return self._model_cache[voice_key]
        try:
            from piper.voice import PiperVoice
            model_path, _ = self.get_voice_file_paths(voice_key)
            if not model_path or (not model_path.exists() and not self.download_voice_files(voice_key)):
                return None
            model = PiperVoice.load(str(model_path))
            self._model_cache[voice_key] = model
            return model
        except ImportError:
            return None
        except Exception:
            return None

    def synthesize_speech(self, text: str, voice_key: str, speaker_id: Optional[int] = None,
                          speed: float = 1.0, noise_scale: float = 0.667, noise_scale_w: float = 0.8) -> Optional[str]:
        if not text or not text.strip():
            return None
        model = self.load_voice_model(voice_key)
        if not model:
            return None

        temp_file_path = None
        try:
            temp_file_path = create_temp_audio_file()

            with wave.open(temp_file_path, 'wb') as wav_file:
                configure_wav_file(wav_file, model.config.sample_rate)

                voice_info = self.voices_config.get(voice_key, {})
                num_speakers = voice_info.get("num_speakers", 1)

                synthesis_kwargs = prepare_synthesis_kwargs(
                    speaker_id, num_speakers, speed, noise_scale, noise_scale_w
                )

                model.synthesize(text, wav_file, **synthesis_kwargs)
            return temp_file_path
        except Exception:
            if temp_file_path:
                cleanup_temp_file(temp_file_path)
            return None
