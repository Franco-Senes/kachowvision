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

#Funcs
def raw_text(
    img: np.ndarray, 
    whitelist: Optional[str] = None, 
    single_char: bool = False
) -> List[str]:
    pass

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