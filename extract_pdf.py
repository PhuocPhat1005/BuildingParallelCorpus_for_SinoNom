# @Contributors: Tu
# Purpose: Extract images from PDF files and enhance them
# Include: enhance_image(image_path), extract_images(pdf_path, output_dir)

# Import libraries
import fitz
import cv2
from PIL import Image
import numpy as np

# Function to enhance images' quality
def enhance_image(
    image_path, # Path to the input image
    gaussian_blur_ksize=(5, 5), # Kernel size for Gaussian Blur
    denoising_h=30, # Strength of Non-Local Means denoising
    denoising_template_window=7, # Template patch size for denoising
    denoising_search_window=21, # Search window size for denoising
    clahe_clip_limit=2.0, # Clip limit for CLAHE
    clahe_tile_grid_size=(8, 8), # Tile grid size for CLAHE
    sharpening_kernel=None, # Custom sharpening kernel
):
    # Load the image in grayscale mode
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: '{image_path}'.")

    # Step 1: Apply Gaussian Blur
    blurred_image = cv2.GaussianBlur(image, gaussian_blur_ksize, 0)

    # Step 2: Denoising with Non-Local Means
    denoised_image = cv2.fastNlMeansDenoising(blurred_image, None, denoising_h, denoising_template_window, denoising_search_window)

    # Step 3: Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=clahe_tile_grid_size)
    contrast_enhanced_image = clahe.apply(denoised_image)

    # Step 4: Sharpening
    if sharpening_kernel is None:
        sharpening_kernel = np.array([[0, -1, 0],
                                       [-1, 5, -1],
                                       [0, -1, 0]])  # Default kernel
    processed_image = cv2.filter2D(contrast_enhanced_image, -1, sharpening_kernel)

    # Convert the processed image to a PIL Image object
    pil_image = Image.fromarray(processed_image)
    return pil_image

# Function to extract images from PDF
def extract_images(pdf_path, output_dir):
    # Open PDF file
    pdf_file = fitz.open(pdf_path)
    
    # Iterate through each page
    for page_num in range(pdf_file.page_count):
        # Get page object
        page = pdf_file[page_num]
        
        # Get image list
        image_list = page.get_images(full=True)
        
        # Iterate through each image
        for image_index, image in enumerate(image_list):
            # Get image data
            xref = image[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Save image to file
            image_path = f"{output_dir}/TayDuKy_page{str(page_num).zfill(3)}.png"
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            
            # Enhance image quality
            enhanced_image = enhance_image(image_path)
            enhanced_image.save(image_path)
    
    # Close PDF file
    pdf_file.close()

# Test main
if __name__ == "__main__":
    # Define input and output paths
    pdf_path = "TayDuKy.pdf"
    output_dir = "output"
    
    # Extract images from PDF
    extract_images(pdf_path, output_dir)
    print("Images extracted successfully!")