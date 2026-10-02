#Libs
import os
from typing import Union, Dict, Any, Tuple, Optional
from pathlib import Path
import cv2
import numpy as np

from Utils.ProcessFinal import isolate_plate_region
from Utils.Extract import (
    _run_ocr_with_boxes,
    extract_license,
    extract_license_number,
    extract_department_letter,
)

#Funcs
def classify_background_color(plate_img: np.ndarray) -> Tuple[str, bool]:
    if plate_img is None or plate_img.size == 0:
        return "unknown", False

    hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # masks
    # blue (electric)
    blue_mask = (h >= 90) & (h <= 135) & (s >= 50) & (v >= 40)
    # green (flexfuel)
    green_mask = (h >= 35) & (h <= 85) & (s >= 50) & (v >= 40)
    # white (combustion)
    white_mask = (s <= 45) & (v >= 50)

    total_pixels = plate_img.shape[0] * plate_img.shape[1]
    blue_ratio = np.count_nonzero(blue_mask) / max(total_pixels, 1)
    green_ratio = np.count_nonzero(green_mask) / max(total_pixels, 1)
    white_ratio = np.count_nonzero(white_mask) / max(total_pixels, 1)

    if blue_ratio > 0.40 and blue_ratio > green_ratio and blue_ratio > white_ratio:
        return "electric", True
    elif green_ratio > 0.40 and green_ratio > blue_ratio and green_ratio > white_ratio:
        return "flexfuel", False
    elif white_ratio > 0.25 and white_ratio > blue_ratio and white_ratio > green_ratio:
        return "combustion", False
    else:
        # Fallback based on relative dominant color ratio
        if blue_ratio >= green_ratio and blue_ratio >= white_ratio and blue_ratio > 0.15:
            return "electric", True
        elif green_ratio >= blue_ratio and green_ratio >= white_ratio and green_ratio > 0.15:
            return "flexfuel", False
        elif white_ratio >= blue_ratio and white_ratio >= green_ratio:
            return "combustion", False
        return "unknown", False


def _resolve_image_path(path_input: Union[str, Path]) -> str:
    path_str = str(path_input)
    if os.path.exists(path_str):
        return path_str

    p = Path(path_str)
    parent = p.parent
    if parent.exists():
        name_lower = p.name.lower()
        for f in parent.iterdir():
            if f.name.lower() == name_lower:
                return str(f)
    return path_str


def analyze_plate(image_path: Union[str, Path, np.ndarray]) -> Dict[str, Any]:
    if isinstance(image_path, (str, Path)):
        img_p = _resolve_image_path(image_path)
        if not os.path.exists(img_p):
            raise FileNotFoundError(f"Image not found at: {image_path}")
        img = cv2.imread(img_p)
        if img is None:
            raise ValueError(f"Failed to load the image at: {img_p}")
    elif isinstance(image_path, np.ndarray):
        img = image_path.copy()
        if img is None or img.size == 0:
            raise ValueError("Failed to copy image or empty array provided")
    else:
        raise TypeError("image_path must be a string, Path, or numpy.ndarray")

    # 1. locate text boxes with OCR
    ocr_boxes = _run_ocr_with_boxes(img)

    # 2. isolate license plate region
    plate_crop = isolate_plate_region(img, ocr_boxes)

    # 3. classify vehicle type and electric status from plate background color
    vehicle_type, is_electric = classify_background_color(plate_crop)

    # 4. extract license plate number
    license_number = extract_license_number(plate_crop, vehicle_type, ocr_boxes)

    # 5. extract department letter and department name
    dept_letter, dept_name = extract_department_letter(img, vehicle_type, ocr_boxes)

    return {
        "license_number": license_number,
        "vehicle_type": vehicle_type,
        "is_electric": is_electric,
        "department_letter": dept_letter,
        "department_name": dept_name,
    }
