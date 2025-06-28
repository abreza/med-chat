import base64
import io
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import pydicom
import nibabel as nib

from app.config.constants import SUPPORTED_MEDICAL_TYPES


def is_medical_file(file_path: str) -> bool:
    file_path_lower = str(file_path).lower()
    return any(file_path_lower.endswith(ext) for ext in SUPPORTED_MEDICAL_TYPES)


def get_medical_file_subtype(file_ext: str) -> str:
    file_ext = file_ext.lower()
    if file_ext in ['.dcm', '.dicom']:
        return 'dicom'
    elif file_ext in ['.nii', '.nii.gz']:
        return 'nifti'
    return 'unknown'


def get_medical_file_info(file_path: str) -> Dict[str, Any]:
    try:
        file_path_lower = str(file_path).lower()

        if file_path_lower.endswith(('.dcm', '.dicom')):
            return _get_dicom_info(file_path)
        elif file_path_lower.endswith(('.nii', '.nii.gz')):
            return _get_nifti_info(file_path)
        else:
            return {"error": "Unsupported medical file type"}

    except Exception as e:
        return {"error": f"Failed to read medical file: {str(e)}"}


def extract_dicom_image(file_path: str, window_center: Optional[float] = None, window_width: Optional[float] = None) -> Optional[str]:
    try:
        ds = pydicom.dcmread(file_path)

        pixel_array = ds.pixel_array.astype(float)

        if window_center is not None and window_width is not None:
            img_min = window_center - window_width // 2
            img_max = window_center + window_width // 2
            pixel_array = np.clip(pixel_array, img_min, img_max)

        pixel_array = ((pixel_array - pixel_array.min()) /
                       (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)

        image = Image.fromarray(pixel_array)
        if len(pixel_array.shape) > 2:
            image = image.convert('RGB')
        else:
            image = image.convert('L')

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return img_str

    except Exception as e:
        print(f"Error extracting DICOM image: {e}")
        return _generate_placeholder_image("DICOM file\n(preview error)")


def extract_nifti_slice(file_path: str, slice_index: int = 50, axis: int = 2) -> Optional[str]:
    try:
        img = nib.load(file_path)
        data = img.get_fdata()

        if axis == 0:
            slice_data = data[min(slice_index, data.shape[0]-1), :, :]
        elif axis == 1:
            slice_data = data[:, min(slice_index, data.shape[1]-1), :]
        else:
            slice_data = data[:, :, min(slice_index, data.shape[2]-1)]

        slice_data = ((slice_data - slice_data.min()) /
                      (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)

        image = Image.fromarray(slice_data)
        image = image.convert('L')

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return img_str

    except Exception as e:
        print(f"Error extracting NIfTI slice: {e}")
        return _generate_placeholder_image("NIfTI file\n(preview error)")


def _get_dicom_info(file_path: str) -> Dict[str, Any]:
    try:
        ds = pydicom.dcmread(file_path)

        return {
            "type": "dicom",
            "patient_name": str(getattr(ds, 'PatientName', 'Unknown')),
            "modality": str(getattr(ds, 'Modality', 'Unknown')),
            "study_date": str(getattr(ds, 'StudyDate', 'Unknown')),
            "series_description": str(getattr(ds, 'SeriesDescription', 'Unknown')),
            "rows": getattr(ds, 'Rows', 0),
            "columns": getattr(ds, 'Columns', 0),
            "bits_allocated": getattr(ds, 'BitsAllocated', 0),
            "pixel_spacing": str(getattr(ds, 'PixelSpacing', 'Unknown'))
        }

    except Exception as e:
        return {"error": f"Failed to read DICOM file: {str(e)}"}


def _get_nifti_info(file_path: str) -> Dict[str, Any]:
    try:
        img = nib.load(file_path)
        header = img.header

        return {
            "type": "nifti",
            "shape": list(img.shape),
            "dimensions": len(img.shape),
            "voxel_size": list(header.get_zooms()),
            "data_type": str(header.get_data_dtype()),
            "orientation": str(nib.aff2axcodes(img.affine)),
            "units": str(header.get_xyzt_units())
        }

    except Exception as e:
        return {"error": f"Failed to read NIfTI file: {str(e)}"}


def _generate_placeholder_image(text: str) -> str:
    try:
        img = Image.new('RGB', (400, 300), color='lightgray')
        draw = ImageDraw.Draw(img)

        font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (400 - text_width) // 2
        y = (300 - text_height) // 2

        draw.text((x, y), text, fill='black', font=font)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return img_str

    except Exception as e:
        print(f"Error generating placeholder image: {e}")
        return None
