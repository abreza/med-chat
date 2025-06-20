import os
import urllib.request
import shutil
import dolphin
from .config import ASR_MODEL_DIR, DOLPHIN_ASSETS_DIR, ASR_MODEL_URLS, ASR_ASSET_URLS

dolphin_model = None
current_dolphin_model_key = "small"


def download_file(url, dest_path):
    if not os.path.exists(dest_path):
        print(f"Downloading {url} to {dest_path}")
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Downloaded {dest_path}")
    else:
        print(f"File already exists: {dest_path}")


def ensure_assets_downloaded():
    for filename, url in ASR_ASSET_URLS.items():
        download_file(url, os.path.join(DOLPHIN_ASSETS_DIR, filename))


def ensure_model_downloaded(model_key):
    if model_key not in ASR_MODEL_URLS:
        raise ValueError(f"Unknown model: {model_key}")

    model_path = os.path.join(ASR_MODEL_DIR, f"{model_key}.pt")
    if not os.path.exists(model_path):
        download_file(ASR_MODEL_URLS[model_key], model_path)

    return model_path


def setup_dolphin_model(model_key="small"):
    global dolphin_model, current_dolphin_model_key

    if dolphin_model is None or current_dolphin_model_key != model_key:
        try:
            print(f"Loading Dolphin ASR model: {model_key}")
            ensure_assets_downloaded()
            ensure_model_downloaded(model_key)

            device = "cuda" if os.environ.get(
                "CUDA_VISIBLE_DEVICES") else "cpu"
            dolphin_model = dolphin.load_model(model_key, ASR_MODEL_DIR, device,
                                               assets_dir=DOLPHIN_ASSETS_DIR)
            current_dolphin_model_key = model_key
            print(f"Dolphin ASR model loaded successfully on {device}")
            return True
        except Exception as e:
            print(f"Error loading Dolphin ASR model: {e}")
            return False
    return True


def get_dolphin_model():
    return dolphin_model
