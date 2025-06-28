import requests
import os
from typing import Optional, Dict, Any, List


class ASRServiceClient:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or os.getenv(
            "ASR_SERVICE_URL", "http://localhost:8002")).rstrip('/')
        self._languages_cache = None
        self._models_cache = None

    def get_languages(self) -> List[Dict[str, Any]]:
        if self._languages_cache is not None:
            return self._languages_cache

        try:
            response = requests.get(f"{self.base_url}/languages", timeout=10)
            response.raise_for_status()
            languages_data = response.json()

            if languages_data.get("success"):
                self._languages_cache = languages_data.get("languages", [])
                return self._languages_cache
            return []

        except requests.RequestException as e:
            print(f"Error fetching languages: {e}")
            return []

    def get_models(self) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            response.raise_for_status()
            models_data = response.json()

            if models_data.get("success"):
                return models_data
            return {}

        except requests.RequestException as e:
            print(f"Error fetching models: {e}")
            return {}

    def transcribe_file(self, file_path: str, language: Optional[str] = None,
                        region: Optional[str] = None, model: str = "small") -> Optional[Dict[str, Any]]:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        try:
            with open(file_path, 'rb') as f:
                files = {"audio": (os.path.basename(
                    file_path), f, "audio/wav")}
                data = {"model": model}

                if language:
                    data["language"] = language
                if region:
                    data["region"] = region

                response = requests.post(
                    f"{self.base_url}/transcribe",
                    files=files,
                    data=data,
                    timeout=60
                )
                response.raise_for_status()

            result = response.json()
            if result.get("success"):
                return {
                    'text': result.get('text', ''),
                    'language': result.get('language'),
                    'region': result.get('region'),
                    'confidence': result.get('confidence')
                }
            return None

        except requests.RequestException as e:
            print(f"ASR transcription error: {e}")
            return None

    def transcribe_base64(self, base64_audio: str, language: Optional[str] = None,
                          region: Optional[str] = None, model: str = "small") -> Optional[Dict[str, Any]]:
        if not base64_audio:
            return None

        try:
            payload = {
                "audio_data": base64_audio,
                "model": model
            }

            if language:
                payload["language"] = language
            if region:
                payload["region"] = region

            response = requests.post(
                f"{self.base_url}/transcribe/base64",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                return {
                    'text': result.get('text', ''),
                    'language': result.get('language'),
                    'region': result.get('region'),
                    'confidence': result.get('confidence')
                }
            return None

        except requests.RequestException as e:
            print(f"ASR transcription error: {e}")
            return None

    def clear_cache(self) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/cache", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
