#Libs
from typing import Tuple, Optional, List
import cv2
import numpy as np

#Funcs

# isolates the plate from the rest of the image
def isolate_plate_region(
    img: np.ndarray, 
    ocr_boxes: Optional[List[Tuple[List, str, float]]] = None
) -> np.ndarray:
    if img is None or img.size == 0:
        return img

    h, w = img.shape[:2]

    if ocr_boxes:
        valid_boxes = []
        for box, txt, score in ocr_boxes:
            pts = np.array(box, dtype=np.float32)
            bx1, by1 = float(pts[:, 0].min()), float(pts[:, 1].min())
            bx2, by2 = float(pts[:, 0].max()), float(pts[:, 1].max())
            area = (bx2 - bx1) * (by2 - by1)
            valid_boxes.append((area, bx1, by1, bx2, by2, txt))

        if valid_boxes:
            valid_boxes.sort(key=lambda x: x[0], reverse=True)
            main_area, mx1, my1, mx2, my2, mtxt = valid_boxes[0]

            group_x1, group_y1, group_x2, group_y2 = mx1, my1, mx2, my2
            main_h = my2 - my1
            for area, bx1, by1, bx2, by2, txt in valid_boxes:
                if abs(by1 - my1) <= max(main_h * 2.2, 50.0):
                    group_x1 = min(group_x1, bx1)
                    group_y1 = min(group_y1, by1)
                    group_x2 = max(group_x2, bx2)
                    group_y2 = max(group_y2, by2)

            gh = group_y2 - group_y1
            gw = group_x2 - group_x1
            pad_y = int(gh * 0.15)
            pad_x = int(gw * 0.10)

            x1 = max(0, int(group_x1 - pad_x))
            y1 = max(0, int(group_y1 - pad_y))
            x2 = min(w, int(group_x2 + pad_x))
            y2 = min(h, int(group_y2 + pad_y))

            cropped = img[y1:y2, x1:x2]
            if cropped.size > 0:
                return cropped

    return img.copy()

# preprocess the plate region to generate multiple variants for OCR
def preprocess_plate_region(roi: np.ndarray, vehicle_type: str = "") -> List[np.ndarray]:
    if roi is None or roi.size == 0:
        return []

    variants: List[np.ndarray] = [roi]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi.copy()
    variants.append(gray)

    # Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    variants.append(enhanced)

    # Otsu thresholding
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)
    variants.append(cv2.bitwise_not(otsu))

    # Adaptive Gaussian thresholding
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    variants.append(adaptive)
    variants.append(cv2.bitwise_not(adaptive))

    return variants
