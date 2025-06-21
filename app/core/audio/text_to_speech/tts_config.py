from pathlib import Path
from dataclasses import dataclass


@dataclass
class TTSConfig:
    data_dir: Path
    model_dir: Path
    base_url: str = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
