# KachowVision 
Bolivian license plate scanner works usinng opencv and ocr.


## Features

- **License Number Detection**: Extracts the license plate automaticaly and in less than 1 second it recognizes the plaque.
- **Vehicle Type Classification**: 
Identifies the vehicle type using the license plate color.
  - **Electric**: Blue background (`vehicle_type: "electric"`, `is_electric: true`)
  - **Flex-Fuel**: Green background (`vehicle_type: "flexfuel"`, `is_electric: false`)
  - **Combustion**: White/metallic background (`vehicle_type: "combustion"`, `is_electric: false`)
- **Department Origin Detection**: 
Detects the cars department using the letter on the top right side.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

# Terminal
```bash
python3 Kachow.py testingimages/Placa-Normal.jpg
```

Output:
```json
{
  "license_number": "5463GBG",
  "vehicle_type": "combustion",
  "is_electric": false,
  "department_letter": "S",
  "department_name": "Santa Cruz",
  "analysis_time_seconds": 0.8421
}
```

The `license_number` field shows the image license plate number.
The `vehicle_type` field shows the vehicle type(electric,flex,combustion)
The `is_electric` field shows if the vehicle is electric.
The `department_letter` field shows the department letter on the top right of the screen
The `department_name` field shows the department name using the department name
The `analysis_time_seconds` field shows how long the image analysis took

### Python

```python
from Kachow import analyze_plate

result = analyze_plate("testingimages/Placa-azul.jpg")
print(result)
```

## Testing

```bash
python3 testing.py
```