from typing import Dict, List, Any, Tuple


def group_files_by_type(files_data: Dict[str, Any]) -> Dict[str, List]:
    grouped = {}
    for file_id, file_info in files_data.items():
        file_type = file_info.get('type', 'unknown')
        if file_type not in grouped:
            grouped[file_type] = []
        grouped[file_type].append((file_id, file_info))
    return grouped


def filter_files_by_type(files_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
    return {
        file_id: file_info
        for file_id, file_info in files_data.items()
        if file_info.get('type') == file_type
    }


def calculate_total_file_size(files_data: Dict[str, Any]) -> int:
    total_size = 0
    for file_info in files_data.values():
        size_str = file_info.get('size', '0 B')
        try:
            size_parts = size_str.split()
            if len(size_parts) >= 2:
                value = float(size_parts[0])
                unit = size_parts[1].upper()
                multipliers = {'B': 1, 'KB': 1024,
                               'MB': 1024**2, 'GB': 1024**3}
                total_size += int(value * multipliers.get(unit, 1))
        except (ValueError, IndexError):
            continue
    return total_size


def group_voices_by_language(voices: Dict[str, Any]) -> Dict[str, List]:
    language_groups = {}
    for voice_key, voice_info in voices.items():
        lang_family = voice_info["language"].get("family", "unknown")
        if lang_family not in language_groups:
            language_groups[lang_family] = []
        language_groups[lang_family].append((voice_info["name"], voice_key))
    return language_groups


def sort_voices_by_quality(voices: List[tuple]) -> List[tuple]:
    return sorted(voices, key=lambda x: x[0])


def extract_selected_files_for_llm(files_data: Dict[str, Any], selected_files: List[str]) -> Tuple[List, List[str]]:
    image_files = []
    text_contents = []
    medical_file_references = []

    for file_id in selected_files:
        if file_id not in files_data:
            continue

        file_info = files_data[file_id]
        file_type = file_info.get('type', 'unknown')
        file_name = file_info.get('name', 'Unknown')

        if file_type == 'image':
            image_files.append(type('File', (), {'name': file_info['path']})())
        elif file_type == 'text':
            content = file_info.get('content', '')
            if content:
                text_contents.append(f"File: {file_name}\n{content}\n")
        elif file_type == 'medical':
            subtype = file_info.get('subtype', 'unknown')
            file_size = file_info.get('size', '0 B')
            medical_file_references.append({
                'name': file_name,
                'type': subtype.upper() if subtype else 'MEDICAL',
                'size': file_size
            })

    if medical_file_references:
        medical_text = "=== MEDICAL FILES REFERENCE ===\n"
        medical_text += "Note: The following medical files are available but their binary content is not included in this analysis:\n\n"

        for med_file in medical_file_references:
            medical_text += f"- {med_file['name']} ({med_file['type']}, {med_file['size']})\n"

        medical_text += "\nFor detailed medical file analysis, please use specialized medical imaging tools.\n\n"
        text_contents.append(medical_text)

    return image_files, text_contents
