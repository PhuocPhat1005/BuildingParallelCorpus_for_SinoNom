# Contributors: Tu
import os
import zipfile
import shutil

def sort_files_in_zip(zip_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    for root, _, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):  
                file_ext = file.split('.')[-1].lower() if '.' in file else "no_extension"
                folder_path = os.path.join(output_dir, file_ext)

                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                base_name = file.split('.')[0]
                if base_name.isdigit():
                    number = int(base_name)
                    if number < 10:
                        new_name = f"TayDuKy_page00{number}"
                    elif number < 100:
                        new_name = f"TayDuKy_page0{number}"
                    else:
                        new_name = f"TayDuKy_page{number}"
                else:
                    new_name = f"TayDuKy_page_{base_name}"

                new_file_path = os.path.join(folder_path, new_name + '.' + file.split('.')[-1])
                
                shutil.move(file_path, new_file_path)




if __name__ == "__main__":
    # Example usage
    zip_file_path = r"data.zip"  
    output_directory = "assets"  
    sort_files_in_zip(zip_file_path, output_directory)