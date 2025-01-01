import os
import re

# Specify the folder containing your files
folder_path = r"TayDuKy\json"

# Specify the book name as the prefix
book_name = "TayDuKy"

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    old_file_path = os.path.join(folder_path, filename)

    # Skip directories
    if os.path.isfile(old_file_path):
        # Add the book name as a prefix and reformat "page_xx" to "pageXXX"
        new_filename = re.sub(r'page_(\d+)', lambda m: f"page{int(m.group(1)):03}", filename)
        new_filename = book_name + new_filename
        new_file_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(old_file_path, new_file_path)

print("Renaming complete!")
