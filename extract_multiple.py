# @Contributors: Tu

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import base64
import json
import os
import time

# API endpoint
url = "https://ocr.kandianguji.com/ocr_api"

# API payload and headers
payload_template = {
    "token": "ed979a49-30e1-4ad2-815c-caf8414c0a5a", 
    "email": "nguyenkimson159357@gmail.com", 
    "image": None,
    "char_ocr": False,
    "det_mode": "hp",
    "image_size": 0,
    "return_position": True,
    "return_choices": False
}
headers = {"Content-Type": "application/json"}

# def process_image(file_path, json_folder):
#     """Process a single image file."""
#     try:
#         with open(file_path, "rb") as image_file:
#             base64_image = base64.b64encode(image_file.read()).decode("utf-8")
#         payload = payload_template.copy()
#         payload["image"] = base64_image
#         response = requests.post(url, json=payload, headers=headers)
#         if response.status_code == 200:
#             response_json = response.json()
#             json_path = os.path.join(json_folder, os.path.basename(file_path).replace(".png", ".json").replace(".jpg", ".json"))
#             with open(json_path, "w", encoding="utf-8") as json_file:
#                 json.dump(response_json, json_file, ensure_ascii=False, indent=4)
#             print(f"Processed: {file_path}")
#         else:
#             print(f"Error {response.status_code} for {file_path}: {response.text}")
#     except Exception as e:
#         print(f"Exception for {file_path}: {e}")


def process_image(file_path, json_folder):
    """Process a single image file, retrying on exception until success."""
    while True:
        try:
            # Đọc và mã hóa hình ảnh thành base64
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Tạo payload cho yêu cầu POST
            payload = payload_template.copy()
            payload["image"] = base64_image
            
            # Gửi yêu cầu POST đến URL
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # Nếu thành công, lưu phản hồi JSON
                response_json = response.json()
                json_filename = os.path.basename(file_path).replace(".png", ".json").replace(".jpg", ".json")
                json_path = os.path.join(json_folder, json_filename)
                
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json.dump(response_json, json_file, ensure_ascii=False, indent=4)
                
                print(f"Đã xử lý thành công: {file_path}")
                break  # Thoát vòng lặp khi thành công
            else:
                # Nếu nhận được mã trạng thái lỗi, in thông báo và tiếp tục thử lại
                print(f"Lỗi {response.status_code} cho {file_path}: {response.text}")
        
        except Exception as e:
            # Nếu gặp ngoại lệ, in thông báo lỗi
            print(f"Exception cho {file_path}: {e}")
        
        # Khoảng nghỉ trước khi thử lại (có thể điều chỉnh thời gian này)
        time.sleep(1)


def get_json(image_folder, json_folder, max_workers=10):
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



# if __name__ == "__main__":
#     get_json(r"assets\images", r"assets\json")
