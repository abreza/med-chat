from typing import List, Tuple

current_language = "fa"
current_region = None


def get_language_options() -> List[Tuple[str, str]]:
    try:
        from dolphin.languages import LANGUAGE_CODES
        language_options = [(f"{code}: {name[0]}", code)
                            for code, name in LANGUAGE_CODES.items()]
        language_options.sort(key=lambda x: x[0])
        return [("Auto-detect", None)] + language_options
    except ImportError:
        return [("Auto-detect", None), ("fa: Persian", "fa"), ("en: English", "en"), ("ar: Arabic", "ar")]


def get_region_options(language: str) -> Tuple[List[Tuple[str, str]], str, bool]:
    if not language:
        return [], None, False
    try:
        from dolphin.languages import LANGUAGE_REGION_CODES
        language_to_regions = {}
        for lang_region, names in LANGUAGE_REGION_CODES.items():
            if "-" in lang_region:
                lang, region = lang_region.split("-", 1)
                if lang not in language_to_regions:
                    language_to_regions[lang] = []
                language_to_regions[lang].append(
                    (f"{region}: {names[0]}", region))

        if language in language_to_regions:
            regions = language_to_regions[language]
            regions.sort(key=lambda x: x[0])
            default_value = regions[0][1] if regions else None
            return regions, default_value, True
    except ImportError:
        pass
    return [], None, False


def update_language_config(language: str, region: str) -> None:
    global current_language, current_region
    current_language = language
    current_region = region
