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
        headers = ["ID", "Image Box", "Text OCR", "Text Char"]
        for col_num, header in enumerate(headers):
            # Sử dụng cả định dạng in đậm và căn giữa cho header
            self.worksheet.write(0, col_num, header, self.workbook.add_format(
                {**self.china_font, 'bold': True, 'align': 'center', 'valign': 'vcenter'}))

        # Đặt độ rộng cho các cột (nếu cần thiết)
        self.worksheet.set_column('A:A', 30)  # ID
        self.worksheet.set_column('B:B', 40)  # Image Box
        self.worksheet.set_column('C:C', 80)  # Text OCR
        self.worksheet.set_column('D:D', 80)  # Text Char

    @staticmethod
    def format_bounding_box(bbox):
        return [tuple(point) for point in bbox]

    def generate_output_excel(self):
        row_num = 1

        for alignment in self.alignment_results:
            page_name = alignment["page_name"]
            id_page = alignment["id_page"]
            id_box = alignment["id_box"]
            bbox = alignment["position"]
            formatted_bbox = ExcelExporterProcessing.format_bounding_box(bbox)
            ocr_text = alignment["ocr_text"]
            aligned_text = alignment["aligned_text"]
            formatted_id_page = str(id_page).zfill(3) if id_page is not None else "000"
            formatted_id_box = str(id_box).zfill(3) if id_box is not None else "000"

            # Column 1: ID
            file_id = f"{page_name}.{formatted_id_page}.{formatted_id_box}"
            self.worksheet.write(row_num, 0, file_id)

            # Column 2: Image Box
            self.worksheet.write(row_num, 1, str(formatted_bbox))

            # Column 3: Text OCR
            self.worksheet.write(row_num, 2, ocr_text, self.default_format)

            # Column 4: Text Char
            self.worksheet.write(row_num, 3, aligned_text, self.default_format)

            row_num += 1

    def close(self):
        self.workbook.close()
        print("Close the workbook.")

def main():
    json_file_path = "output_text.json"
    alignment_results = load_alignment_results(json_file_path)

    output_file_path = "output.xlsx"

    excel_exporter = ExcelExporterProcessing(output_file_path, alignment_results)
    excel_exporter.setup_headers()
    excel_exporter.generate_output_excel()
    excel_exporter.close()

    print("DONE")

if __name__ == '__main__':
    main()