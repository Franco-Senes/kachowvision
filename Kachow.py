#Libs
import os
import sys
import json 
import argparse
import time
from typing import Union, Dict, Any
from pathlib import Path
import cv2
import numpy as np

from Utils.Analyze import analyze_plate

__all__ = ["analyze_plate", "main"]

def main():
    parser = argparse.ArgumentParser(
        description="KachowVision"
    )
    print("[+ Debug] Current working directory:", os.getcwd())
    parser.add_argument("image", nargs="?", type=str, help="path to image")
    parser.add_argument("--json", action="store_true", default=True, help="output for json")


    args = parser.parse_args()
    print("[+ Debug] Image selected:", parser.parse_args().image)
    if not args.image:
        parser.print_help()
        print("Please provide an image.")
        return
    print("[+ Debug] Analyzing image:", args.image)
    try:
        start_time = time.perf_counter()
        result = analyze_plate(args.image)
        result["analysis_time_seconds"] = round(time.perf_counter() - start_time, 4)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        raise SystemExit(1)

if __name__ == "__main__":
    main()