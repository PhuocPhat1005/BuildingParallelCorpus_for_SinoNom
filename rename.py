import os
import re

# Specify the folder containing your files
folder_path = r"assets\json"

# Specify the book name as the prefix
book_name = "TayDuKy"

def rename_json(folder_path):
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        old_file_path = os.path.join(folder_path, filename)

        # Skip directories
        if os.path.isfile(old_file_path):
            # Add the book name as a prefix and reformat "page_xx" to "pageXXX"
            new_filename = re.sub(r'_page(\d+)', lambda m: f"_page{int(m.group(1)):03}", filename)
            new_filename = new_filename
            new_file_path = os.path.join(folder_path, new_filename)

            # Rename the file
            os.rename(old_file_path, new_file_path)

    print("Renaming complete!")
