#Libs
import os
import re
from typing import Tuple, Optional, List, Union
import cv2
import numpy as np

from Utils.ProcessFinal import preprocess_plate_region

# Department map
# each license plate in bolivia has a letter in the license plate which is located
# up on the top right corner of the license plate we can locate the department of the car with this.
DEPARTMENT_MAP = {
    "B": "Beni",
    "C": "Cochabamba",
    "H": "Chuquisaca",
    "L": "La Paz",
    "N": "Pando",
    "O": "Oruro",
    "P": "Potosí",
    "S": "Santa Cruz",
    "T": "Tarija",
}

DIGIT_TO_LETTER_MAP = {
    "0": "O", "1": "I", "2": "Z", "4": "A", "5": "S", "6": "G", "8": "B"
}

LETTER_TO_DIGIT_MAP = {
    "O": "0", "I": "1", "Z": "2", "A": "4", "S": "5", "G": "6", "B": "8", "Q": "0", "D": "0"
}

_PYTESSERACT_AVAILABLE = False
_RAPID_OCR = None

# init ocr
try:
    from rapidocr_onnxruntime import RapidOCR
    _RAPID_OCR = RapidOCR()
except Exception:
    try:
        from rapidocr import RapidOCR
        _RAPID_OCR = RapidOCR()
    except Exception:
        _RAPID_OCR = None

# tesseract available check
try:
    import pytesseract
    _PYTESSERACT_AVAILABLE = True
except Exception:
    _PYTESSERACT_AVAILABLE = False


#Funcs
# runs ocr and it returns a list of boxes text and score
def _run_ocr_with_boxes(img: np.ndarray) -> List[Tuple[List, str, float]]:
    boxes = []
    if _RAPID_OCR is not None and img is not None and img.size > 0:
        try:
            ocr_in = img if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            res, _ = _RAPID_OCR(ocr_in)
            if res:
                for line in res:
                    if len(line) >= 3:
                        boxes.append((line[0], str(line[1]), float(line[2])))
                    elif len(line) == 2:
                        boxes.append((line[0], str(line[1]), 1.0))
        except Exception:
            pass
    return boxes

ocr_boxes = _run_ocr_with_boxes


def raw_text(
    img: np.ndarray, 
    whitelist: Optional[str] = None, 
    single_char: bool = False
) -> List[str]:
    texts = []
    if img is None or img.size == 0:
        return texts

    # rapidocr
    if _RAPID_OCR is not None:
        try:
            ocr_in = img if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if single_char and hasattr(_RAPID_OCR, 'text_rec'):
                rec_res, _ = _RAPID_OCR.text_rec(ocr_in)
                if rec_res:
                    for item in rec_res:
                        txt = str(item[0]).strip()
                        if txt:
                            texts.append(txt)
            else:
                res, _ = _RAPID_OCR(ocr_in)
                if res:
                    for line in res:
                        if len(line) >= 2 and line[1]:
                            texts.append(str(line[1]).strip())
        except Exception:
            pass

    # tesseract
    if _PYTESSERACT_AVAILABLE:
        try:
            psm = 10 if single_char else 7
            cfg = f"--psm {psm} --oem 3"
            if whitelist:
                cfg += f" -c tessedit_char_whitelist={whitelist}"
            tess_txt = pytesseract.image_to_string(img, config=cfg).strip()
            if tess_txt:
                texts.append(tess_txt)
        except Exception:
            pass

    return texts


# clean useless info from the license plate
def clean_registration_text(raw_text: str) -> Optional[str]:
    cleaned = re.sub(r'[^A-Z0-9]', '', raw_text.upper())
    if "BOLIVIA" in cleaned:
        cleaned = cleaned.replace("BOLIVIA", "")

    patterns = [
        r'(\d{4})([A-Z]{3})',
        r'(\d{3})([A-Z]{3})',
    ]
    for pat in patterns:
        m = re.search(pat, cleaned)
        if m:
            return f"{m.group(1)}{m.group(2)}"

    # character repair for the 7-char plates (4 numbers and 3 letters)  
    if len(cleaned) == 7:
        d = "".join(LETTER_TO_DIGIT_MAP.get(c, c) for c in cleaned[:4])
        l = "".join(DIGIT_TO_LETTER_MAP.get(c, c) for c in cleaned[4:])
        if d.isdigit() and l.isalpha():
            return f"{d}{l}"

    # character repair for the 6-char plates (3 numbers and 3 letters)
    if len(cleaned) == 6:
        d = "".join(LETTER_TO_DIGIT_MAP.get(c, c) for c in cleaned[:3])
        l = "".join(DIGIT_TO_LETTER_MAP.get(c, c) for c in cleaned[3:])
        if d.isdigit() and l.isalpha():
            return f"{d}{l}"

    return None


# extract the department letter on the top right of the plate and finds the department
def extract_department_letter(
    img: np.ndarray,
    vehicle_type: str,
    ocr_boxes: Optional[List[Tuple[List, str, float]]] = None
) -> Tuple[Union[str, bool], Union[str, bool]]: 
    if vehicle_type != "combustion" or img is None or img.size == 0:
        return False, False

    h, w = img.shape[:2]

    # 1. search ocr boxes in the upper half of the plate
    if ocr_boxes:
        for box, text, _ in ocr_boxes:
            pts = np.array(box, dtype=np.float32)
            center_x = np.mean(pts[:, 0])
            center_y = np.mean(pts[:, 1])

            # check if the box is in the upper half of the plate and right half
            if center_y < 0.50 * h and center_x > 0.50 * w:
                clean = re.sub(r'[^A-Z]', '', text.upper()).replace("BOLIVIA", "")
                if len(clean) == 1 and clean in DEPARTMENT_MAP:
                    return clean, DEPARTMENT_MAP[clean]

        # Check directly above department sticker serial numbers (e.g., '317259')
        for box, text, _ in ocr_boxes:
            pts = np.array(box, dtype=np.float32)
            center_x = np.mean(pts[:, 0])
            center_y = np.mean(pts[:, 1])
            cleaned_digits = re.sub(r'\D', '', text)
            if len(cleaned_digits) >= 4 and center_y < 0.50 * h and center_x > 0.55 * w:
                bx1, bx2 = int(np.min(pts[:, 0])), int(np.max(pts[:, 0]))
                by1, by2 = int(np.min(pts[:, 1])), int(np.max(pts[:, 1]))
                bh, bw = by2 - by1, bx2 - bx1
                y1 = max(0, by1 - int(bh * 2.4))
                y2 = max(0, by1 - 2)
                x1 = bx1 + int(bw * 0.05)
                x2 = bx2 - int(bw * 0.05)
                roi = img[y1:y2, x1:x2]
                if roi.size > 0:
                    for txt in raw_text(roi, single_char=True):
                        clean = re.sub(r'[^A-Z]', '', txt.upper())
                        if len(clean) == 1 and clean in DEPARTMENT_MAP:
                            return clean, DEPARTMENT_MAP[clean]
                        for ch in clean:
                            if ch in DEPARTMENT_MAP:
                                return ch, DEPARTMENT_MAP[ch]

    # 2. multicrop scanning the upper region
    cropconfigs = [
        (0.18, 0.32, 0.78, 0.96),
        (0.00, 0.40, 0.60, 0.99),
        (0.15, 0.35, 0.75, 0.95),
        (0.00, 0.45, 0.50, 0.99),
    ]

    for (y1_f, y2_f, x1_f, x2_f) in cropconfigs:
        y1, y2 = int(y1_f * h), int(y2_f * h)
        x1, x2 = int(x1_f * w), int(x2_f * w)
        dept_roi = img[y1:y2, x1:x2]
        if dept_roi.size == 0:
            continue
        
        dept_scaled = cv2.resize(dept_roi, (0, 0), fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        for txt in raw_text(dept_scaled, single_char=True):
            clean = re.sub(r'[^A-Z]', '', txt.upper()).replace("BOLIVIA", "")
            if len(clean) == 1 and clean in DEPARTMENT_MAP:
                return clean, DEPARTMENT_MAP[clean]
            for ch in clean:
                if ch in DEPARTMENT_MAP:
                    return ch, DEPARTMENT_MAP[ch]

        variants = preprocess_plate_region(dept_scaled, vehicle_type) 
        for variant in variants:
            results = raw_text(variant, whitelist="BCDFGHJKLMNPRSTVXZ", single_char=True)
            for txt in results:
                clean = re.sub(r'[^A-Z]', '', txt.upper()).replace("BOLIVIA", "")
                if len(clean) == 1 and clean in DEPARTMENT_MAP:
                    return clean, DEPARTMENT_MAP[clean]
                for ch in clean:
                    if ch in DEPARTMENT_MAP:
                        return ch, DEPARTMENT_MAP[ch]

    return False, False


def extract_license(
    plate_img: np.ndarray,
    vehicle_type: str,
    ocr_boxes: Optional[List[Tuple[List, str, float]]] = None
) -> Optional[str]:
    candidates = []

    # 1. from ocr boxes
    if ocr_boxes:
        for box, txt, score in ocr_boxes:
            cleaned = clean_registration_text(txt)
            if cleaned:
                pts = np.array(box, dtype=np.float32)
                area = (pts[:, 0].max() - pts[:, 0].min()) * (pts[:, 1].max() - pts[:, 1].min())
                # Prioritize: 7-character standard plates, larger bounding box area, OCR confidence score
                priority = (len(cleaned) == 7, area, score)
                candidates.append((priority, cleaned))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    # 2. direct ocr
    if plate_img is not None and plate_img.size > 0:
        variants = preprocess_plate_region(plate_img, vehicle_type)
        for variant in variants:
            for txt in raw_text(variant):
                cleaned = clean_registration_text(txt)
                if cleaned:
                    return cleaned

    return None

extract_license_number = extract_license