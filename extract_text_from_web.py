# @Contributors: Thai

import ast
from bs4 import BeautifulSoup
import re
import requests
import os
from difflib import SequenceMatcher
from BBox import BBoxes_of_JSON
from rapidfuzz import fuzz, process
from multiprocessing import Pool
import json
import pandas as pd
import difflib
import csv



URL_WEBSITE = "https://www.gutenberg.org/cache/epub/23962/pg23962-images.html"


def is_cjk(char):
    # if character is Sino-Nom/Chinese (CJK blocks)
    return any([
        '\u4E00' <= char <= '\u9FFF',    # CJK Unified Ideographs
        '\u3400' <= char <= '\u4DBF',    # CJK Unified Ideographs Extension A
        '\u20000' <= char <= '\u2A6DF',  # CJK Unified Ideographs Extension B
        '\u2A700' <= char <= '\u2EBEF',  # CJK Unified Ideographs Extension C-F
        '\uF900' <= char <= '\uFAFF',    # CJK Compatibility Ideographs
    ])


def crawl_text_from_web(raw_text_path="./data/raw_text.txt"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(URL_WEBSITE, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {URL_WEBSITE}")
        return ""

    text = ""
    soup = BeautifulSoup(response.content, "html.parser")
    all_p_tags = soup.find_all("p", id=True) 

    for idx, p_tag in enumerate(all_p_tags):
        if idx == 0: 
            continue
        temp = p_tag.get_text(strip=True)  
        if temp:
            text += temp + ""  

    with open(raw_text_path, "w", encoding='utf-8') as file:
        file.write(text)


def clean_text(raw_text_path="./data/raw_text.txt", clean_text_path = "./data/clean_text.txt"):
    
    with open(raw_text_path, "r", encoding='utf-8') as file:
        raw_text = file.read()
    clean_text = raw_text.replace('\t', '').replace('\n', '').strip()
    clean_text = "".join(raw_text.split()) 
    clean_text = ''.join(char for char in clean_text if is_cjk(char))

    with open(clean_text_path, "w", encoding='utf-8') as file:
        file.write(clean_text)



def calculate_match_score(ocr_text, candidate):
    sequence_matcher = difflib.SequenceMatcher(None, ocr_text, candidate)
    
    matching_blocks = sequence_matcher.get_matching_blocks()

    matching_chars = sum(block.size for block in matching_blocks)

    if len(ocr_text) > 0:
        score = matching_chars / len(ocr_text)
    else:
        score = 0

    return score



def find_best_match_rapidfuzz(ocr_text, ground_text, start_idx):
    best_match_text = ""
    best_match_score = 0
    best_match_idx = 0
    score = 0
    i = 0
    while i < len(ground_text):
        candidate = ground_text[i:i + len(ocr_text)]
        score = calculate_match_score(ocr_text, candidate)  # RapidFuzz ratio: 0 đến 1

        if score > best_match_score:
            best_match_text = candidate
            best_match_score = score
            best_match_idx = i
        
        i += 1

    print(f"OCR text: {ocr_text}")
    print(f"Need check: {ground_text}")
    if best_match_score > 0.3:
        pos1, pos2 = align_strings(ocr_text, best_match_text)
        if pos1 == None or pos2 == None:
            print("======================")
            return "", start_idx
        number_of_redundant_char = len(ocr_text) - 1 - pos1
        new_pos_best_match_text = pos2 + number_of_redundant_char
        cut_best_match_text = ground_text[best_match_idx:best_match_idx+new_pos_best_match_text + 1]
        new_pos_best_match_text = best_match_idx+pos2 + number_of_redundant_char
        print(f"Best match: {cut_best_match_text}")
        print("======================")
        return cut_best_match_text, start_idx + new_pos_best_match_text + 1
    print("======================")
    return "", start_idx



def align_bboxes_with_true_text(listBBox, true_ground_text):

    list_pair_boxes = []
    current_index = 0

    for box in listBBox:
        ocr_text = box.get_cleaned_text()
        if len(ocr_text) < 15:
            max_search_len = len(ocr_text) + 3
        else:
            max_search_len = len(ocr_text) + 170
        ground_text = true_ground_text[current_index:current_index+max_search_len]
        best_match, new_index = find_best_match_rapidfuzz(ocr_text, ground_text, current_index)
        list_pair_boxes.append((box, best_match))
        current_index = new_index
    

    return list_pair_boxes





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
            "ocr_text": bbox.get_base_text(),
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
            if true_text == "":
                continue  
            
            writer.writerow([bbox.get_cleaned_text(), true_text])





def main():
    # dir_name = "data"
    # os.makedirs(dir_name, exist_ok=True) 
    # print(f"Directory '{dir_name}' created successfully.")
    # crawl_text_from_web("./data/raw_text.txt")
    # clean_text(raw_text_path = "./data/raw_text.txt", clean_text_path="./data/clean_text.txt")

    with open("./data/clean_text.txt", 'r', encoding='utf-8') as cleanText:
        true_ground_text = cleanText.read()
    listBBox = []
    directory = 'assets/json/'
    pattern = r'^TayDuKy_page\d{3}\.json$'
    for filename in os.listdir(directory):
        if re.match(pattern, filename):
            full_file_path = os.path.join(directory, filename)
            with open(full_file_path, "rb") as json_file:
                temp = BBoxes_of_JSON(json_file.read(), filename)
                listBBox += temp

    # print(len(listBBox))
    # for _bbox in listBBox:
    #     print(_bbox.get_position(), _bbox.get_cleaned_text())

    aligned_boxes = align_bboxes_with_true_text(listBBox, true_ground_text)

    aligned_text_json = "output_text.json"
    dump_aligned_boxes_to_json(aligned_boxes, output_text_json=aligned_text_json)


    align_text_csv = "ocr_corrections.csv"
    dump_aligned_boxes_to_csv(aligned_boxes, align_text_csv)


if __name__ == "__main__":
    main()
