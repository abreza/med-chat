import requests
import tempfile
import os
from typing import Optional, Dict, Any


class TTSServiceClient:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or os.getenv(
            "TTS_SERVICE_URL", "http://localhost:8001")).rstrip('/')
        self._voices_cache = None

    def get_voices(self) -> Dict[str, Any]:
        if self._voices_cache is not None:
            return self._voices_cache

        try:
            response = requests.get(f"{self.base_url}/voices", timeout=10)
            response.raise_for_status()
            voices_data = response.json()

            if voices_data.get("success"):
                self._voices_cache = voices_data.get("voices", {})
                return self._voices_cache
            return {}

        except requests.RequestException as e:
            print(f"Error fetching voices: {e}")
            return {}

    def synthesize_speech(self, text: str, voice_key: str, speaker_id: int = 0,
                          speed: float = 1.0, noise_scale: float = 0.667,
                          noise_scale_w: float = 0.8) -> Optional[str]:
        if not text or not text.strip():
            return None

        try:
            payload = {
                "text": text,
                "voice_key": voice_key,
                "speaker_id": speaker_id,
                "speed": speed,
                "noise_scale": noise_scale,
                "noise_scale_w": noise_scale_w
            }

            response = requests.post(
                f"{self.base_url}/synthesize",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()

            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False)
            temp_file.write(response.content)
            temp_file.close()

            return temp_file.name

        except requests.RequestException as e:
            print(f"TTS synthesis error: {e}")
            return None

    def clear_cache(self) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/cache", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
