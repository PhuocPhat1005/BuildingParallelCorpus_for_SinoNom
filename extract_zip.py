# Contributors: Tu
import os
import zipfile
import shutil

def sort_files_in_zip(zip_path, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    # Sort files into folders by extension
    for root, _, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):  # Ensure it's a file
                file_ext = file.split('.')[-1].lower() if '.' in file else "no_extension"
                folder_path = os.path.join(output_dir, file_ext)

                # Create the folder for the extension if it doesn't exist
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                # Move the file to the appropriate folder
                shutil.move(file_path, os.path.join(folder_path, file))



if __name__ == "__main__":
    # Example usage
    zip_file_path = r"ocr_result.zip"  # Replace with your zip file path
    output_directory = "sorted_data"   # Replace with your desired output directory
    sort_files_in_zip(zip_file_path, output_directory)