# @Contributors: Lê Phước Phát
# Purpose: Dùng để dóng hàng từng chữ trong box
# Include: class DictionaryLoader, class TextAlignment, def load_alignment_result

import pandas as pd
import json
import os
import re
# import opencc

def load_alignment_results(json_file_path: str):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            alignment_results = json.load(file)
        return alignment_results
    except FileNotFoundError:
        print(f"File {json_file_path} does not exist!")
        return None
    except json.JSONDecodeError as e:
        print(f"File {json_file_path} cannot be decoded: {e}")
        return None

class DictionaryLoader:
    def __init__(self, sino_dict_file):
        self.sino_dict_file = sino_dict_file

    def load_dictionaries(self):
        sino_similar_df = pd.read_excel(self.sino_dict_file)
        sinonom_dict = self._process_sinonom_dict(sino_similar_df)
        return sinonom_dict

    def _process_sinonom_dict(self, df):
        sinonom_dict = {}
        for _, row in df.iterrows():
            key = row['Input Character']
            raw_chars = row['Top 20 Similar Characters'].strip("[]")
            similar_chars = [char.strip(" '") for char in raw_chars.split(",")]
            similar_chars.insert(0, key)
            sinonom_dict[key] = similar_chars
        return sinonom_dict

class TextAlignment:
    def __init__(self, sinonom_dict, alignment_bbox_results):
        self.sinonom_dict = sinonom_dict
        self.alignment_bbox_results = alignment_bbox_results
        # self.converter = opencc.OpenCC('t2s')

    def get_similar_set(self, sinonom_char):
        return self.sinonom_dict.get(sinonom_char, set())

    def preprocess_text(self, text):
        if not text:
            return ""
        chinese_only = re.findall(r"[\u4e00-\u9fa5]+", text)
        chinese_text = ''.join(chinese_only)
        # simplified_text = self.converter.convert(chinese_text)
        return chinese_text

    def align_characters(self, china_ocr_text, china_origin_text):
        # Xử lý trường hợp chuỗi rỗng
        if not china_ocr_text and not china_origin_text:
            return [{"ocr_char": None, "origin_char": None, "status": "Empty"}]
        if not china_ocr_text:
            return [{"ocr_char": None, "origin_char": char, "status": "Inserted (No OCR)"} for char in china_origin_text]
        if not china_origin_text:
            return [{"ocr_char": char, "origin_char": None, "status": "Deleted (No Text)"} for char in china_ocr_text]

        # Dóng hàng bằng thuật toán (trường hợp cả hai không rỗng)
        ocr_char = list(china_ocr_text)
        origin_char = list(china_origin_text)
        m, n = len(ocr_char), len(origin_char)

        dp = [[0] * (n + 1) for _ in range(m + 1)]
        operations = [[None] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            dp[i][0] = i
            operations[i][0] = "delete"
        for j in range(1, n + 1):
            dp[0][j] = j
            operations[0][j] = "insert"

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ocr_char[i - 1] == origin_char[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                    operations[i][j] = "match"
                else:
                    replace = dp[i - 1][j - 1] + 1
                    insert = dp[i][j - 1] + 1
                    delete = dp[i - 1][j] + 1
                    min_operation = min(replace, insert, delete)

                    dp[i][j] = min_operation
                    if min_operation == replace:
                        operations[i][j] = "replace"
                    elif min_operation == insert:
                        operations[i][j] = "insert"
                    else:
                        operations[i][j] = "delete"

        aligned_chars = []
        i, j = m, n
        while i > 0 or j > 0:
            operation = operations[i][j]
            ocr_c = ocr_char[i - 1] if i > 0 else None
            origin_c = origin_char[j - 1] if j > 0 else None

            if operation == "match":
                aligned_chars.append({"ocr_char": ocr_c, "origin_char": origin_c, "status": "No Color"})
                i -= 1
                j -= 1
            elif operation == "replace":
                aligned_chars.append({"ocr_char": ocr_c, "origin_char": origin_c, "status": "Red Color"})
                i -= 1
                j -= 1
            elif operation == "insert":
                aligned_chars.append({"ocr_char": None, "origin_char": origin_c, "status": "Inserted (No OCR)"})
                j -= 1
            elif operation == "delete":
                aligned_chars.append({"ocr_char": ocr_c, "origin_char": None, "status": "Deleted (No Text)"})
                i -= 1

        aligned_chars.reverse()
        return aligned_chars

    def calculate_alignment(self):
        alignment_results = []

        for item in self.alignment_bbox_results:
            page_name = item["page_name"]
            id_page = item["id_page"]
            id_box = item["id_box"]
            china_ocr_text = item.get("ocr_text", "")
            china_origin_text = item.get("aligned_text", "")
            bbox = item["position"]

            alignment = self.align_characters(
                self.preprocess_text(china_ocr_text),
                self.preprocess_text(china_origin_text)
            )
            alignment_results.append({
                "page_name": page_name,
                "id_page": id_page,
                "id_box": id_box,
                "bounding_box": bbox,
                "china_ocr_text": self.preprocess_text(china_ocr_text),
                "china_origin_text": self.preprocess_text(china_origin_text),
                "alignment": alignment
            })

        alignment_text_file = "align_text.json"
        json_alignment_result = json.dumps(alignment_results, ensure_ascii=False, indent=4)

        with open(alignment_text_file, "w", encoding="utf-8") as json_file:
            json_file.write(json_alignment_result)

        return alignment_results

def main():
    json_file_path = "output_text.json"
    alignment_bbox_results = load_alignment_results(json_file_path)

    sinonom_dict_filename = "SinoNom_similar_Dic.xlsx"
    dictionaries = DictionaryLoader(sinonom_dict_filename)
    sinonom_dict = dictionaries.load_dictionaries()

    text_alignment_processor = TextAlignment(sinonom_dict, alignment_bbox_results)
    char_alignment_results = text_alignment_processor.calculate_alignment()

    print("DONE")

if __name__ == '__main__':
    main()
