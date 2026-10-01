#Libs
import os
import re
from typing import Tuple, Optional, List
import cv2
import numpy as np

# Department map
# each license plate in bolivia has a letter in the license plate which is located
# up on the top left corner of the license plate we can locate the department of the car with this.
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

_PYTESSERACT_AVAILABLE = False # PYTESSERACT available and on check
_RAPID_OCR = None # RAPID OCR available and on check

# init ocr
try:
    from rapidocr import RapidOCR
    _RAPID_OCR = RapidOCR()
except Exception: # if rapidocr not install tell the user isnt installed and them set rapidocr to None
    print("Rapidocr isnt installed or available, trying to use tesseract instead")
    _RAPID_OCR = None
# 

# tesseract available check
try:
    import pytesseract
    _PYTESSERACT_AVAILABLE = True
except Exception:
    _PYTESSERACT_AVAILABLE = False
#Funcs
def raw_text(
    img: np.ndarray, 
    whitelist: Optional[str] = None, 
    single_char: bool = False
) -> List[str]:
    texts = []
    # select if to use rapid ocr or tesseract ocr is used i prefer ocr

    # ocr
    if RAPID_OCR is not None:
        try:
            ocr_in = img if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            res, _ = _RAPID_OCR(ocr_in)
            if res:
                for line in res:
                    if len(line) >= 2 and line[1]:
                        texts.append(str(line[1]).strip())
        except Exception:
            pass
    # tesseract
    if _PYTESSERACT_AVAILABLE: # AI GENERATED CHUNK OF CODE HERE:
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
    
def clean_registration_text(
    raw_text: str) -> Optional[str]:

def extract_department_letter(
    img: np.ndarray,
    vehicle_type: str,
    ocr_boxes: Optional[List[Tuple[List, str, float]]] = None
) -> Tuple[Optional[str], Optional[str]]: 

def extract_license_number(
    plate_img: np.ndarray,
    vehicle_type: str,
    ocr_boxes: Optional[List[Tuple[List, str, float]]] = None
) -> Optional[str]: