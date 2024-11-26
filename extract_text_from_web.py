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




def find_best_match_rapidfuzz(ocr_text, ground_text, start_idx, SinoNom_similar_Dictionary):
    max_search_len = len(ocr_text) + 5 
    ground_window = ground_text[start_idx : start_idx + max_search_len]
    best_match_text = ""
    best_match_score = 0
    best_match_idx = 0

    def are_similar(char_a, char_b):
        setA = set(SinoNom_similar_Dictionary.get(char_a, [char_a]))
        setB = set(SinoNom_similar_Dictionary.get(char_b, [char_b]))
        return not setA.isdisjoint(setB) 

    for i in range(len(ground_window) - len(ocr_text) + 1):
        candidate = ground_window[i : i + len(ocr_text)]

        matching_chars = sum(1 for a, b in zip(ocr_text, candidate) if are_similar(a, b))

        score = matching_chars / len(ocr_text)

        if score > best_match_score:
            best_match_text = candidate
            best_match_score = score
            best_match_idx = i

    if best_match_score > 0.3:  
        return best_match_text, start_idx + best_match_idx + len(best_match_text)

    return "", start_idx



def align_bboxes_with_true_text(listBBox, true_ground_text, SinoNom_similar_Dictionary):

    list_pair_boxes = []
    current_index = 0

    for box in listBBox:
        ocr_text = box.get_cleaned_text()
        best_match, new_index = find_best_match_rapidfuzz(ocr_text, true_ground_text, current_index, SinoNom_similar_Dictionary)
        list_pair_boxes.append((box, best_match))
        current_index = new_index
    

    return list_pair_boxes


def dump_aligned_boxes_to_json(aligned_pairs):
    enriched_boxes = []

    for bbox, true_text in aligned_pairs:
        enriched_box = {
            "page_name": bbox.get_page_name(),
            "id_page": bbox.get_id_page(),
            "id_box": bbox.get_id_box(),  
            "position": bbox.get_position(),
            "ocr_text": bbox.get_base_text(),
            "aligned_text": true_text
        }
        enriched_boxes.append(enriched_box)
    

    with open("output_text.json", 'w', encoding='utf-8') as json_file:
        json.dump(enriched_boxes, json_file, ensure_ascii=False, indent=4)


def load_SinoNom_similar_pairs(file_path="SinoNom_similar_Dic.xlsx"):
    df = pd.read_excel(file_path, engine='openpyxl')
    sinonim_dict = {}

    for _, row in df.iterrows():
        key = row[df.columns[0]]  # The key in the first column
        try:
            values = ast.literal_eval(row[df.columns[1]])  # Convert to list of characters
        except (ValueError, SyntaxError):
            values = []  

        sinonim_dict[key] = values  

    return sinonim_dict





def main():
    # dir_name = "data"
    # os.makedirs(dir_name, exist_ok=True) 
    # print(f"Directory '{dir_name}' created successfully.")
    # crawl_text_from_web("./data/raw_text.txt")
    # clean_text(raw_text_path = "./data/raw_text.txt", clean_text_path="./data/clean_text.txt")

    SinoNom_dict_path = "SinoNom_similar_Dic.xlsx"
    SinoNom_similar_Dictionary = load_SinoNom_similar_pairs(SinoNom_dict_path)



    with open("./data/clean_text.txt", 'r', encoding='utf-8') as cleanText:
        true_ground_text = cleanText.read()
    

    listBBox = []
    listPage = ["TayDuKy_page048.json"]
    for _page in listPage:
        with open(_page, "rb") as json_file:
            temp = (BBoxes_of_JSON(json_file.read(), _page))
            listBBox += temp

    # print(len(listBBox))
    for _bbox in listBBox:
        print(_bbox.get_position(), _bbox.get_cleaned_text())

    aligned_boxes = align_bboxes_with_true_text(listBBox, true_ground_text, SinoNom_similar_Dictionary)


    # for _align in aligned_boxes:
    #     print(_align)

    dump_aligned_boxes_to_json(aligned_boxes)

if __name__ == "__main__":
    main()