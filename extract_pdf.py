# @Contributors: Tu
# Purpose: Extract images from PDF files and enhance them
# Include: enhance_image(image_path), extract_images(pdf_path, output_dir)

# Import libraries
import fitz
import cv2
from PIL import Image
import numpy as np
import os
from multiprocessing import Pool, cpu_count




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

    # Step 1: Apply Gaussian Blur
    blurred_image = cv2.GaussianBlur(image, gaussian_blur_ksize, 0)

    # Step 2: Denoising with Non-Local Means
    denoised_image = cv2.fastNlMeansDenoising(
        blurred_image, None, denoising_h, denoising_template_window, denoising_search_window
    )

    # Step 3: Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=clahe_tile_grid_size)
    contrast_enhanced_image = clahe.apply(denoised_image)

    # Step 4: Sharpening
    if sharpening_kernel is None:
        sharpening_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    processed_image = cv2.filter2D(contrast_enhanced_image, -1, sharpening_kernel)

    # Step 5: Invert colors if necessary
    mean_intensity = np.mean(processed_image)
    if mean_intensity < 128:  # Adjust this threshold based on your data
        processed_image = 255 - processed_image

    # Convert the processed image to a PIL Image object
    pil_image = Image.fromarray(processed_image)
    return pil_image


# # Function to extract images from PDF
# def extract_images(pdf_path, output_dir):


#     # Make sure the image dir is created before store in it
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)


#     # Open PDF file
#     pdf_file = fitz.open(pdf_path)
    
#     # Iterate through each page
#     for page_num in range(pdf_file.page_count):
#         # Get page object
#         page = pdf_file[page_num]
        
#         # Get image list
#         image_list = page.get_images(full=True)
        
#         # Iterate through each image
#         for image_index, image in enumerate(image_list):
#             # Get image data
#             xref = image[0]
#             base_image = pdf_file.extract_image(xref)
#             image_bytes = base_image["image"]
            
#             # Save image to file
#             image_path = f"{output_dir}/TayDuKy_page{page_num + 1}.png"
#             with open(image_path, "wb") as image_file:
#                 image_file.write(image_bytes)
            
#             # Enhance image quality
#             enhanced_image = enhance_image(image_path)
#             enhanced_image.save(image_path)
    
#     # Close PDF file
#     pdf_file.close()


def process_and_save_image(args):
    output_dir, pdf_name, page_num, image_index, image_bytes = args
    try:
        # Tạo tên file duy nhất cho mỗi hình ảnh
        if page_num + 1 < 10:
            image_path = os.path.join(
                output_dir, f"{pdf_name}_page00{page_num + 1}.png"
            )
        elif page_num + 1 < 100:
            image_path = os.path.join(
                output_dir, f"{pdf_name}_page0{page_num + 1}.png"
            )
        else:
            image_path = os.path.join(
                output_dir, f"{pdf_name}_page{page_num + 1}.png"
            )

        # Lưu hình ảnh gốc vào file
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)

        # Gọi hàm enhance_image để tăng cường chất lượng hình ảnh
        enhanced_image = enhance_image(image_path)

        # Lưu hình ảnh đã được tăng cường trở lại file
        enhanced_image.save(image_path)

        print(f"Lưu hình ảnh: {image_path}")
    except Exception as e:
        print(f"Lỗi khi xử lý hình ảnh trang {page_num + 1}, hình {image_index + 1}: {e}")

# Hàm rút trích hình ảnh từ PDF sử dụng multiprocessing
def extract_images(pdf_path, output_dir, num_of_pages=None):
    # Đảm bảo thư mục lưu hình ảnh tồn tại
    os.makedirs(output_dir, exist_ok=True)

    # Mở tệp PDF
    pdf_file = fitz.open(pdf_path)
    pages = pdf_file.page_count
    if num_of_pages != None and num_of_pages >= 1 or num_of_pages <= pdf_file.page_count:
        pages = num_of_pages

    # Tạo danh sách các tác vụ xử lý hình ảnh
    tasks = []

    # Lặp qua từng trang
    for page_num in range(pages):
        page = pdf_file[page_num]
        image_list = page.get_images(full=True)

        # Lặp qua từng hình ảnh trong trang
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]

            # Thêm vào danh sách các tác vụ
            tasks.append((output_dir, pdf_path[:-4], page_num, image_index, image_bytes))

    pdf_file.close()

    if not tasks:
        print("Không tìm thấy hình ảnh nào trong tệp PDF.")
        return

    # Xác định số tiến trình tối đa
    num_processes = min(cpu_count(), len(tasks))

    # Sử dụng multiprocessing Pool để xử lý các hình ảnh song song
    with Pool(processes=num_processes) as pool:
        pool.map(process_and_save_image, tasks)

    print("Hoàn thành việc rút trích và xử lý hình ảnh.")






# Test main
# if __name__ == "__main__":
#     # Define input and output paths
#     pdf_path = "TayDuKy.pdf"
#     output_dir = r"assets\images"
    
#     # Extract images from PDF
#     extract_images(pdf_path, output_dir)
#     print("Images extracted successfully!")