from dolphin.languages import LANGUAGE_CODES, LANGUAGE_REGION_CODES

import os

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

ASR_MODEL_DIR = os.path.join(DATA_DIR, "dolphin/models")
os.makedirs(ASR_MODEL_DIR, exist_ok=True)

DOLPHIN_ASSETS_DIR = os.path.join(DATA_DIR, "dolphin/assets")
os.makedirs(DOLPHIN_ASSETS_DIR, exist_ok=True)

ASR_MODELS = {
    "base (140M)": "base",
    "small (372M)": "small",
}

ASR_MODEL_URLS = {
    "base": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/base.pt",
    "small": "https://huggingface.co/DataoceanAI/dolphin-small/resolve/main/small.pt",
}

ASR_ASSET_URLS = {
    "bpe.model": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/bpe.model",
    "config.yaml": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/config.yaml",
    "feats_stats.npz": "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/feats_stats.npz",
}

language_options = [(f"{code}: {name[0]}", code)
                    for code, name in LANGUAGE_CODES.items()]
language_options.sort(key=lambda x: x[0])
language_options = [("Auto-detect", None)] + language_options

language_to_regions = {}
for lang_region, names in LANGUAGE_REGION_CODES.items():
    if "-" in lang_region:
        lang, region = lang_region.split("-", 1)
        if lang not in language_to_regions:
            language_to_regions[lang] = []
        language_to_regions[lang].append((f"{region}: {names[0]}", region))

current_language = "fa"
current_region = None
