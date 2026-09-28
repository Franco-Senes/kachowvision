#coded with ai gemini
import json
import subprocess
import sys

tests = [
    (
        "testingimages/Placa-azul.jpg",
        {
            "license_number": "6328YIS",
            "vehicle_type": "electric",
            "is_electric": True,
            "department_letter": False,
            "department_name": False,
        },
    ),
    (
        "testingimages/Placa-normal.jpg",
        {
            "license_number": "5463CBG",
            "vehicle_type": "combustion",
            "is_electric": False,
            "department_letter": "S",
            "department_name": "Santa Cruz",
        },
    ),
    (
        "testingimages/Placa-verde.jpg",
        {
            "license_number": "6339ZTX",
            "vehicle_type": "flexfuel",
            "is_electric": False,
            "department_letter": False,
            "department_name": False,
        },
    ),
]

for img, expected in tests:
    cmd = [sys.executable, "Kachow.py", img]
    res = subprocess.run(cmd, capture_output=True, text=True)

    json_str = res.stdout[res.stdout.find("{") :]
    actual = json.loads(json_str)

    assert actual == expected, (
        f"FAILED: {img}\nExpected: {expected}\nGot: {actual}"
    )
    print(f"PASSED: {img}")

print("All tests passed!")