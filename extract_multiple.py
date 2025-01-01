# @Contributors: Tu

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import base64
import json
import os

# API endpoint
url = "https://ocr.kandianguji.com/ocr_api"

# API payload and headers
payload_template = {
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

def process_image(file_path, json_folder):
    """Process a single image file."""
    try:
        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        payload = payload_template.copy()
        payload["image"] = base64_image
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            json_path = os.path.join(json_folder, os.path.basename(file_path).replace(".png", ".json").replace(".jpg", ".json"))
            with open(json_path, "w", encoding="utf-8") as json_file:
                json.dump(response_json, json_file, ensure_ascii=False, indent=4)
            print(f"Processed: {file_path}")
        else:
            print(f"Error {response.status_code} for {file_path}: {response.text}")
    except Exception as e:
        print(f"Exception for {file_path}: {e}")

def get_json(image_folder, json_folder, max_workers=5):
    """Process all image files in parallel."""
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    image_files = [
        os.path.join(image_folder, file)
        for file in os.listdir(image_folder)
        if file.endswith(".png") or file.endswith(".jpg")
    ]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_image, file, json_folder) for file in image_files]
        for future in as_completed(futures):
            try:
                future.result()  # Wait for each thread to complete
            except Exception as e:
                print(f"Error in thread: {e}")

if __name__ == "__main__":
    get_json(r"assets\images", r"assets\json")
