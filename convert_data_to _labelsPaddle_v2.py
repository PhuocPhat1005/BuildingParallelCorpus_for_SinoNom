import pandas as pd
import re
import ast
import numpy as np


# Hàm sắp xếp các điểm theo quy tắc top-left → top-right → bottom-right → bottom-left
def sort_box(points):
    points = np.array(points)  # Chuyển sang numpy array
    sorted_indices = np.lexsort((points[:, 0], points[:, 1]))  # Sắp xếp theo y trước, sau đó x
    top_two = points[sorted_indices[:2]]  # Lấy 2 điểm trên cùng
    bottom_two = points[sorted_indices[2:]]  # Lấy 2 điểm dưới cùng

    # Xác định top-left và top-right
    top_two = top_two[np.argsort(top_two[:, 0])]  # Sắp xếp theo x
    top_left, top_right = top_two[0], top_two[1]

    # Xác định bottom-left và bottom-right
    bottom_two = bottom_two[np.argsort(bottom_two[:, 0])]  # Sắp xếp theo x
    bottom_left, bottom_right = bottom_two[0], bottom_two[1]

    # Kết hợp theo quy tắc
    return [top_left.tolist(), top_right.tolist(), bottom_right.tolist(), bottom_left.tolist()]
# Đọc file Excel
result_file_path = './output.xlsx'
df = pd.read_excel(result_file_path)

for i in range(len(df["ID"])):
    df["ID"][i] = df["ID"][i][:-4]
    df["ID"][i] = str(df["ID"][i]).replace(".","_page")
    df["ID"][i] += ".png"

# Cột chứa tọa độ box (giả sử tên cột là "Box")
df['Sorted_Box'] = df['Image Box'].apply(lambda x: sort_box(ast.literal_eval(x)))  # Chuyển string sang list và sắp xếp

# Xuất file Excel mới
result_file_path_sorted = './result_sorted.xlsx'
df.to_excel(result_file_path_sorted, index=False)
# Đọc dữ liệu từ file Excel
input_file_path = "./result_sorted.xlsx"  # Thay bằng đường dẫn file của bạn
df = pd.read_excel(input_file_path)

# Nhóm dữ liệu theo Page_ID
grouped = df.groupby('ID')

# Tạo danh sách để lưu kết quả
result = []

for page_id, group in grouped:
    page_result = []

    for _, row in group.iterrows():
        points = eval(row['Sorted_Box'])  # Chuyển chuỗi tọa độ thành danh sách
        transcription = row['Text OCR']
        page_result.append({"transcription": transcription, "points": points})

    # Tạo chuỗi cho Page_ID
    result_string = "[" + ", ".join(
        [f'{{"transcription": "{item["transcription"]}", "points": {item["points"]},"difficult": false}}' for item in page_result]
    ) + "]"

    # Thêm Page_ID và kết quả vào danh sách
    result.append(f"images/{page_id}\t{result_string}")

# Lưu kết quả vào file .txt
output_path = "./Label.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(result))

print(f"Đã chuyển đổi dữ liệu và lưu vào {output_path}")


# def main():
#     #result_file_path = './output.xlsx'
#     #df = pd.read_excel(result_file_path)

#     #df = df.head(10)
#     df = {"ID":["TayDuKy.001.001"
# ,"TayDuKy.001.002","TayDuKy.001.003",
# "TayDuKy.001.004",
# "TayDuKy.001.005",
# "TayDuKy.001.006",
# "TayDuKy.001.007",
# "TayDuKy.001.008",
# "TayDuKy.001.009",
# "TayDuKy.002.009",
# "TayDuKy.001.010"]}

#     for row in df["ID"]:
#         row = row[:-4]
#         row = str(row).replace(".","_page")
#         row += ".png"
#         print(row)

# if __name__ == "__main__":
#     main()