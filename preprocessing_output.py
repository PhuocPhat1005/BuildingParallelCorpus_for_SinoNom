# @Contributors: Le Phuoc Phat
import pandas as pd
import json
from xlsxwriter.workbook import Workbook
import os
import re

def load_alignment_results(json_file_path: str):
    try:
        with open(json_file_path, 'r', encoding = 'utf-8') as file:
            alignment_results = json.load(file)
        return alignment_results
    except FileNotFoundError:
        print(f"File {json_file_path} does not exist !!!")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing json file {json_file_path}: {e}")
        return None

class ExcelExporterProcessing:
    def __init__(self, output_file_path: str, alignment_results: dict):
        self.output_file_path = output_file_path
        self.alignment_results = alignment_results
        if self.alignment_results is None:
            raise ValueError("No alignment results can be created because JSON data is invalid or not existed.")
        self.workbook = Workbook(self.output_file_path)
        self.worksheet = self.workbook.add_worksheet()

        self.china_font = {'font_name': 'SimSun'}
        self.bold_format = self.workbook.add_format({**self.china_font, 'bold': True})
        self.green_text_format = self.workbook.add_format({**self.china_font, 'color': '#00FF00'})  # Xanh lá
        self.red_text_format = self.workbook.add_format({**self.china_font, 'color': '#FF0000'})  # Đỏ
        self.blue_text_format = self.workbook.add_format({**self.china_font, 'color': '#0000FF'})  # Xanh dương
        self.default_format = self.workbook.add_format(self.china_font)  # Định dạng mặc định

    def setup_headers(self):
        headers = ["Image_name", "ID", "Image Box", "Text OCR", "Text Char"]
        for col_num, header in enumerate(headers):
            # Sử dụng cả định dạng in đậm và căn giữa cho header
            self.worksheet.write(0, col_num, header, self.workbook.add_format(
                {**self.china_font, 'bold': True, 'align': 'center', 'valign': 'vcenter'}))

        # Đặt độ rộng cho các cột (nếu cần thiết)
        self.worksheet.set_column('A:A', 25)  # ID
        self.worksheet.set_column('B:B', 16)  # ID
        self.worksheet.set_column('C:C', 47)  # Image Box
        self.worksheet.set_column('D:D', 60)  # Text OCR
        self.worksheet.set_column('E:E', 60)  # Text Char

    @staticmethod
    def format_bounding_box(bbox):
        return [tuple(point) for point in bbox]

    def write_green_text(self, row, col, text):
        rich_text = []
        for char in text:
            rich_text.extend([self.green_text_format, char]) # Mỗi ký tự kèm định dạng xanh lá

        self.worksheet.write_rich_string(row, col, *rich_text)

    def write_china_ocr(self, row, col, ocr_text, alignment):
        rich_text = []

        # Nếu có văn bản OCR
        if ocr_text:
            for i, char in enumerate(ocr_text):
                # Lấy status của từng ký tự từ alignment hoặc gán mặc định nếu thiếu
                status = alignment[i]["status"] if i < len(alignment) else "No Color"

                # Chọn định dạng màu sắc dựa trên status
                if status == "No Color":
                    rich_text.append(self.default_format)
                    rich_text.append(char)  # Ký tự không định dạng
                else:
                    rich_text.append(self.red_text_format)
                    rich_text.append("[MASK]")

        # Kiểm tra nếu rich_text có ít hơn 2 phần tử
        if len(rich_text) <= 2:
            # Thêm ký tự ảo và định dạng mặc định
            rich_text.append(self.default_format)
            rich_text.append(" ")  # Ký tự ảo (dấu cách)

        # Ghi toàn bộ chuỗi rich text với các định dạng vào Excel
        self.worksheet.write_rich_string(row, col, *rich_text)

    def generate_output_excel(self):
        row_num = 1

        for alignment in self.alignment_results:
            page_name = alignment["page_name"]
            id_page = alignment["id_page"]
            id_box = alignment["id_box"]
            bbox = alignment["bounding_box"]
            formatted_bbox = ExcelExporterProcessing.format_bounding_box(bbox) if bbox is not None else None
            ocr_text = alignment["china_ocr_text"] or ""
            aligned_text = alignment["china_origin_text"] or ""
            formatted_id_page = str(id_page).zfill(3) if id_page is not None else "000"
            formatted_id_box = str(id_box).zfill(3) if id_box is not None else "000"
            alignment_box = alignment["alignment"]

            # Column 1: Image_name
            image_name = f"{page_name}_page{formatted_id_page}.png"
            self.worksheet.write(row_num, 0, image_name)

            # Column 2: ID
            file_id = f"{page_name}.{formatted_id_page}.{formatted_id_box}"
            self.worksheet.write(row_num, 1, file_id)

            # Column 2: Image Box
            self.worksheet.write(row_num, 2, str(formatted_bbox))

            # Column 3: Text OCR
            self.write_china_ocr(row_num, 3, ocr_text, alignment_box)

            # Column 4: Text Char
            self.worksheet.write(row_num, 4, aligned_text, self.default_format)

            row_num += 1

    def close(self):
        self.workbook.close()
        print("Close the workbook.")

def main():
    json_file_path = "align_text.json"
    alignment_results = load_alignment_results(json_file_path)

    output_file_path = "output_test.xlsx"

    excel_exporter = ExcelExporterProcessing(output_file_path, alignment_results)
    excel_exporter.setup_headers()
    excel_exporter.generate_output_excel()
    excel_exporter.close()

    print("DONE")

if __name__ == '__main__':
    main()