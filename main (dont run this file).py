import requests
import base64
import json
import cv2
import numpy as np
from PIL import Image
import os



# API endpoint
url = "https://ocr.kandianguji.com/ocr_api"


file_image = 'test.jpeg'


base64_image = None




def noise_reduction(image_path, brightness=100, contrast=0.3, dilation_iterations=2):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh tại đường dẫn '{image_path}'.")

    # Tăng độ sáng và độ tương phản
    adjusted = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

    # Loại bỏ nhiễu bằng Median Blur
    denoised = cv2.medianBlur(adjusted, ksize=1)

    # Áp dụng Gaussian Blur để giảm nhiễu
    blurred = cv2.GaussianBlur(denoised, (3, 1), 0)

    # Binarization sử dụng phương pháp Otsu
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Đảm bảo chữ là màu đen trên nền trắng
    black_pixels = cv2.countNonZero(cv2.bitwise_not(binary))
    white_pixels = binary.size - black_pixels
    if black_pixels > white_pixels:
        binary = cv2.bitwise_not(binary)

    # Dilation để làm chữ đậm hơn
    kernel = np.ones((2,2), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=dilation_iterations)

    cv2.imwrite(image_path, binary)
    return image_path



def resize_image(image_path, max_size=1000, output_file=None):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            total_size = width + height

            if total_size > max_size:
                scale_factor = max_size / total_size
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                img.save(image_path)
                print(f"Resized image '{image_path}' to {new_width}x{new_height}")
                if output_file:
                    output_file.write(f"{os.path.basename(image_path)}\n")
            else:
                print(f"Image '{image_path}' does not need resizing.")
    except Exception as e:
        print(f"[!] Error resizing image '{image_path}': {e}")








# with open(file_image, "rb") as image_file:

#     # resize_image(file_image)

#     base64_image = base64.b64encode(image_file.read()).decode("utf-8")
#     print(base64_image)

# payload = {
#     "token": "467d35f5-62c7-481b-b386-c4ae9836c78d", 
#     "email": "nguyenkimson159357@gmail.com", 
#     "image": base64_image,
#     "char_ocr": False,
#     "det_mode": "auto",
#     "image_size": 0,
#     "return_position": True,
#     "return_choices": False
# }

# headers = {"Content-Type": "application/json"}

# # Make the POST request
# response = requests.post(url, json=payload, headers=headers)

# # Debugging: Check the raw response content
# print("Raw Response Content:", response.text)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the JSON response
#     print(response)
#     response_json = response.json()

#     # Save the response to a .json file
#     with open("temp.json", "w", encoding="utf-8") as file:
#         json.dump(response_json, file, ensure_ascii=False, indent=4)

#     print("Response saved to temp.json")
# else:
#     print(f"Error: {response.status_code}, {response.text}")