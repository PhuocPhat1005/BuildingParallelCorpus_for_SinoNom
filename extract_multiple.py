from concurrent.futures import ThreadPoolExecutor, as_completed
import fitz
import os
import cv2
import numpy as np
from PIL import Image
import base64
import json
import requests

# Function to enhance images' quality
def enhance_image(
    image_path,
    gaussian_blur_ksize=(5, 5),
    denoising_h=30,
    denoising_template_window=7,
    denoising_search_window=21,
    clahe_clip_limit=2.0,
    clahe_tile_grid_size=(8, 8),
    sharpening_kernel=None,
):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: '{image_path}'.")
    blurred_image = cv2.GaussianBlur(image, gaussian_blur_ksize, 0)
    denoised_image = cv2.fastNlMeansDenoising(
        blurred_image, None, denoising_h, denoising_template_window, denoising_search_window
    )
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=clahe_tile_grid_size)
    contrast_enhanced_image = clahe.apply(denoised_image)
    if sharpening_kernel is None:
        sharpening_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    processed_image = cv2.filter2D(contrast_enhanced_image, -1, sharpening_kernel)
    mean_intensity = np.mean(processed_image)
    if mean_intensity < 128:
        processed_image = 255 - processed_image
    return Image.fromarray(processed_image)

# Function to extract images from PDF with multiprocessing and renaming
def function_extract_images(pdf_path, output_dir, max_workers=8):
    pdf_file = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    book_name = os.path.splitext(os.path.basename(pdf_path))[0]

    def process_page(page_num):
        page = pdf_file[page_num]
        image_list = page.get_images(full=True)
        extracted_files = []
        for image_index, image in enumerate(image_list):
            xref = image[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_filename = f"{book_name}_page{page_num + 1:03}.png"
            image_path = os.path.join(output_dir, image_filename)
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            enhanced_image = enhance_image(image_path)
            enhanced_image.save(image_path)
            extracted_files.append(image_path)
        return extracted_files

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_page, page_num) for page_num in range(pdf_file.page_count)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing page: {e}")
    pdf_file.close()

# Function to process images and call the OCR API
def function_extract_json(image_folder, json_folder, max_workers=8):
    os.makedirs(json_folder, exist_ok=True)
    image_files = [
        os.path.join(image_folder, file)
        for file in os.listdir(image_folder)
        if file.endswith(".png") or file.endswith(".jpg")
    ]

    def process_image(file_path):
        try:
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            payload = {
                "token": "467d35f5-62c7-481b-b386-c4ae9836c78d",
                "email": "nguyenkimson159357@gmail.com",
                "image": base64_image,
                "char_ocr": False,
                "det_mode": "auto",
                "image_size": 0,
                "return_position": True,
                "return_choices": False,
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post("https://ocr.kandianguji.com/ocr_api", json=payload, headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                json_path = os.path.join(json_folder, os.path.basename(file_path).replace(".png", ".json"))
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json.dump(response_json, json_file, ensure_ascii=False, indent=4)
                print(f"Processed: {file_path}")
            else:
                print(f"Error {response.status_code} for {file_path}: {response.text}")
        except Exception as e:
            print(f"Exception for {file_path}: {e}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_image, file) for file in image_files]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in thread: {e}")

# Main function to manage folders and execute tasks
if __name__ == "__main__":
    pdf_path = "TayDuKy.pdf"
    assets_folder = "assets"
    images_folder = "images"
    jsons_folder = "json"
    a = os.path.join(assets_folder, images_folder)
    b = os.path.join(assets_folder, jsons_folder)
    function_extract_images(pdf_path, a, max_workers=8)
    function_extract_json(a, b, max_workers=8)
