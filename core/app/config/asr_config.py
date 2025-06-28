from typing import List, Tuple
from app.clients.asr import ASRServiceClient

current_language = "fa"
current_region = None
asr_client = ASRServiceClient()


def get_language_options() -> List[Tuple[str, str]]:
    try:
        languages = asr_client.get_languages()
        if not languages:
            return [
                ("Auto-detect", None),
                ("fa: Persian", "fa"),
                ("en: English", "en"),
                ("ar: Arabic", "ar")
            ]

        language_options = []
        for lang_info in languages:
            code = lang_info.get("code")
            name = lang_info.get("name")
            if code and name:
                language_options.append((f"{code}: {name}", code))

        language_options.sort(key=lambda x: x[0])
        return [("Auto-detect", None)] + language_options

    except Exception as e:
        print(f"Error getting language options: {e}")
        return [
            ("Auto-detect", None),
            ("fa: Persian", "fa"),
            ("en: English", "en"),
            ("ar: Arabic", "ar")
        ]


def get_region_options(language: str) -> Tuple[List[Tuple[str, str]], str, bool]:
    if not language:
        return [], None, False

    try:
        languages = asr_client.get_languages()
        for lang_info in languages:
            if lang_info.get("code") == language:
                regions = lang_info.get("regions", [])
                if regions:
                    region_options = []
                    for region_info in regions:
                        code = region_info.get("code")
                        name = region_info.get("name")
                        if code and name:
                            region_options.append((f"{code}: {name}", code))

                    region_options.sort(key=lambda x: x[0])
                    default_value = region_options[0][1] if region_options else None
                    return region_options, default_value, True

        return [], None, False

    except Exception as e:
        print(f"Error getting region options: {e}")
        return [], None, False


def update_language_config(language: str, region: str) -> None:
    global current_language, current_region
    current_language = language
    current_region = region
