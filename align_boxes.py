# @Contributor: Thai


import re
from BBox import BBoxes_of_JSON
import os
import difflib
from difflib import SequenceMatcher
import csv
import json
import opencc

converter = opencc.OpenCC('t2s.json') 





def convert_hanzi_strings(str1):
    str1_simplified = converter.convert(str1)
    return str1_simplified

def calculate_match_score(ocr_text, candidate):
    sequence_matcher = difflib.SequenceMatcher(None, ocr_text, candidate)
    
    matching_blocks = sequence_matcher.get_matching_blocks()

    matching_chars = sum(block.size for block in matching_blocks)

    if len(ocr_text) > 0:
        score = matching_chars / len(ocr_text)
    else:
        score = 0
    return score





def align_strings(str1, str2):
    sequence_matcher = difflib.SequenceMatcher(None, str1, str2)
    
    matching_blocks = sequence_matcher.get_matching_blocks()
    
    for block in reversed(matching_blocks):
        a_start, b_start, size = block.a, block.b, block.size
        
        for i in range(size - 1, -1, -1): 
            c1 = str1[a_start + i]
            c2 = str2[b_start + i]
            
            if c1 == c2:
                pos_str1 = a_start + i
                pos_str2 = b_start + i
                return pos_str1, pos_str2
    
    return None, None


def find_best_match_rapidfuzz(ocr_text, ground_text, start_idx):
    best_match_text = ""
    best_match_score = 0
    best_match_idx = 0
    score = 0
    i = 0
    hanzi_ocr_text = convert_hanzi_strings(ocr_text)
    hanzi_ground_text = convert_hanzi_strings(ground_text)
    while i < len(ground_text):
        candidate = hanzi_ground_text[i:i + len(hanzi_ocr_text)]
        score = calculate_match_score(hanzi_ocr_text, candidate)  # RapidFuzz ratio: 0 đến 1

        if score > best_match_score:
            best_match_text = candidate
            best_match_score = score
            best_match_idx = i
        
        i += 1
    if best_match_score > 0.35:
        pos1, pos2 = align_strings(hanzi_ocr_text, best_match_text)
        if pos1 == None or pos2 == None:
            return "", start_idx
        number_of_redundant_char = 0
        new_pos_best_match_text = pos2 + number_of_redundant_char
        cut_best_match_text = ground_text[best_match_idx:best_match_idx+new_pos_best_match_text + 1]
        new_pos_best_match_text = best_match_idx+pos2 + number_of_redundant_char
        return cut_best_match_text, start_idx + new_pos_best_match_text + 1
    return "", start_idx







def align_bboxes_with_true_text(listBBox, true_ground_text):

    list_pair_boxes = []
    current_index = 0
    for box in listBBox:
        ocr_text = box.get_cleaned_text()
        if len(ocr_text) < 15:
            max_search_len = len(ocr_text) + 5
        else:
            max_search_len = len(ocr_text) + 180
        ground_text = true_ground_text[current_index:current_index+max_search_len]
        best_match, new_index = find_best_match_rapidfuzz(ocr_text, ground_text, current_index)
        list_pair_boxes.append((box, best_match))
        current_index = new_index

    return list_pair_boxes





def dump_aligned_boxes_to_json(aligned_pairs, output_text_json = "output_text.json"):
    enriched_boxes = []

    for bbox, true_text in aligned_pairs:
        if true_text == "":
            continue
        enriched_box = {
            "page_name": bbox.get_page_name(),
            "id_page": bbox.get_id_page(),
            "id_box": bbox.get_id_box(),  
            "position": bbox.get_position(),
            "ocr_text": bbox.get_cleaned_text(),
            "aligned_text": true_text
        }
        enriched_boxes.append(enriched_box)
    

    with open(output_text_json, 'w', encoding='utf-8') as json_file:
        json.dump(enriched_boxes, json_file, ensure_ascii=False, indent=4)

def dump_aligned_boxes_to_csv(aligned_pairs, output_file = "ocr_corrections.csv"):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        writer.writerow(["OCR Text", "Ground Text"])
        
        for bbox, true_text in aligned_pairs:
            writer.writerow([bbox.get_cleaned_text(), true_text])






# def main():
#     with open("./data/clean_text.txt", 'r', encoding='utf-8') as cleanText:
#         true_ground_text = cleanText.read()


#     listBBox = []
#     directory = 'assets/json/'
#     pattern = r'^TayDuKy_page\d{3}\.json$'
#     for filename in os.listdir(directory):
#         if re.match(pattern, filename):
#             full_file_path = os.path.join(directory, filename)
#             with open(full_file_path, "rb") as json_file:
#                 listBBox += BBoxes_of_JSON(json_file.read(), filename)


#     aligned_boxes = align_bboxes_with_true_text(listBBox, true_ground_text)

#     aligned_text_json = "output_text.json"
#     dump_aligned_boxes_to_json(aligned_boxes, output_text_json=aligned_text_json)


#     align_text_csv = "ocr_corrections.csv"
#     dump_aligned_boxes_to_csv(aligned_boxes, align_text_csv)


# if __name__ == "__main__":
#     main()
