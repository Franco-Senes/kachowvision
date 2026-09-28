#Libs
import os
from typing import Union, Dict, Any
from pathlib import Path
import cv2
import numpy as np

from Utils.ProcessFinal import isolate_plate_region
from Utils.Extract import (
    _run_ocr_with_boxes,
    extract_license,
    extract_department_letter,
)

#Funcs
def classify_background_color(plate_img: np.ndarray) -> Tuple[str, bool]:
    hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    #masks
    #blue
    blue_mask = (h >= 90) & (h <= 135) & (s >= 50) & (v >= 40)
    #green
    green_mask = (h >= 35) & (h <= 85) & (s >= 50) & (v >= 40)
    #white
    white_mask = (s <= 45) & (v >= 50)

    total_pixels = plate_img.shape[0] * plate_img.shape[1]
    blue_ratio = np.count_nonzero(blue_mask) / max(total_pixels, 1)
    green_ratio = np.count_nonzero(green_mask) / max(total_pixels, 1)
    white_ratio = np.count_nonzero(white_mask) / max(total_pixels, 1)

    if blue_ratio > 0.40 and blue_ratio > green_ratio and blue_ratio > white_ratio:
        return "electric", True
    elif green_ratio > 0.40 and green_ratio > blue_ratio and green_ratio > white_ratio:
        return "flexfuel", True
    elif white_ratio > 0.40 and white_ratio > blue_ratio and white_ratio > green_ratio:
        return "combustion", True
    else:
        return "unknown", False

def analyze_plate(image_path: Union[str, Path, np.ndarray]) -> Dict[str, Any]: #implement later
if isinstance(image_path, (str, Path)):
    img_p = str(image_path)
    if not os.path.exists(img_p):
        raise FileNotFoundError(f"Image not found at: {img_p}")
    img = cv2.imread(img_p)
    if img is None:
        raise ValueError(f"Failed to load the image at: {img_p}")
    elif isinstance(image_path, np.ndarray):
        img = image_path.copy()
    if img is None:
        raise ValueError("Failed to copy the image")
    else:
        raise TypeError("image_path must be a string, Path, or numpy.ndarray")

    ocr_boxes = _run_ocr_with_boxes(img)
    plate_crop = isolate_plate_region(img, ocr_boxes)
    vehicle_type, is_electric = classify_background_color(plate_crop)
    license_number = extract_license_number(plate_crop, vehicle_type, ocr_boxes)
    dept_letter = extract_department_letter(plate_crop, vehicle_type, ocr_boxes)

    return {
        "license_number": license_number,
        "vehicle_type": vehicle_type,
        "is_electric": is_electric,
        "department_letter": dept_letter,
        "department_name": dept_name,
    }

