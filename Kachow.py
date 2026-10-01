#Libs
import os
import json 
import argparse
from typing import Union, Dict, Any
from pathlib import Path
import cv2
import numpy as np

#Func
def analyze_plate(image_path: Union[str, Path, np.ndarray]) -> Dict[str, Any]:
    if isinstance(image_path, (str, Path)):
        img_p = str(image_path)
        if not os.path.exists(img_p):
            raise FileNotFoundError(f"Image not found {img_p}")
        img = cv2.imread(img_p)
        if img is None:
            raise ValueError(f"Failed to load image: {img_p}")
    elif isinstance(image_path, np.ndarray):
        img = image_path.copy()
    else:
        raise TypeError("this isnt a filepath or array ):. please provide a valid image path or numpy array.")

    # locate text boxes
    ocr_boxes = _run_ocr_with_boxes(img) #implement Utils/analyze.py
    print("[1] Located ocr boxes", ocr_boxes)
    # isolate license plate
    plate_crop = isolate_plate_region(img, ocr_boxes) #implement Utils/ProcessFinal.py
    print("[2] Isolated license plate", plate_crop)
    # classify vehicle type
    vehicle_type, is_electric = classify_background_color(plate_crop) #implement Utils/ProcessFinal.py
    print("[3] Classified vehicle type", vehicle_type, is_electric)
    # extract the license plate
    license = extract_license(plate_crop, vehicle_type, ocr_boxes) #implement Utils/Extract.py
    print("[4] Extracted license plate", license)
    # the department letter and name finally
    dept_letter, dept_name = extract_department_letter(img, vehicle_type, ocr_boxes) #implement Utils/Extract.py
    print("[5] Extracted department letter and name", dept_letter, dept_name)

    # return everything with json
    return {
        "license_number": license,
        "vehicle_type": vehicle_type,
        "is_electric": is_electric,
        "department_letter": dept_letter,
        "department_name": dept_name,
    }
def main():
    parser = argparse.ArgumentParser(
        description="KachowVision - license plate scanner only works with Bolivian license plates"
    )
    parser.add_argument("image", nargs="?", type=str, help="path to image ")
    parser.add_argument("--json", action="store_true", default=True, help="output for json")

    args = parser.parse_args()

    if not args.image:
        parser.print_help()
        print("Please provide an image.")
        return

    try:
        result = analyze_plate(args.image)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e), "indent":2}))
        raise SystemExit(1)

if __name__ == "__main__":
    main()