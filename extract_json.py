# @Contributors:  Tu
# Purpose: Call API, extract JSON data, and return the result
# Include: get_json(image_folder, json_folder)

# Import libraries
import requests
import base64
import json
import os

# API endpoint
url = "https://ocr.kandianguji.com/ocr_api"

# Api handling
payload = {
    "token": "467d35f5-62c7-481b-b386-c4ae9836c78d", 
    "email": "nguyenkimson159357@gmail.com", 
    "image": None,
    "char_ocr": False,
    "det_mode": "auto",
    "image_size": 0,
    "return_position": True,
    "return_choices": False
}

headers = {"Content-Type": "application/json"}

# Make the POST request
response = requests.post(url, json=payload, headers=headers)

def get_json(image_folder, json_folder):
    for file in os.listdir(image_folder):
        if file.endswith(".png"):
            with open(os.path.join(image_folder, file), "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                payload["image"] = base64_image
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    response_json = response.json()
                    with open(os.path.join(json_folder, file.replace(".png", ".json")), "w", encoding="utf-8") as file:
                        json.dump(response_json, file, ensure_ascii=False, indent=4)
                    print(f"Response saved")
                else:
                    print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    get_json("output", "json_folder")