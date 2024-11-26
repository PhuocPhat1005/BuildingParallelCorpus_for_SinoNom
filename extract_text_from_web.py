# @Contributors: Thai


from bs4 import BeautifulSoup
import re
import requests
import os
from difflib import SequenceMatcher
from BBox import BBoxes_of_JSON
from rapidfuzz import fuzz, process
from multiprocessing import Pool
import json



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




def find_best_match_rapidfuzz(ocr_text, ground_text, start_idx):
    max_search_len = len(ocr_text)+0
    ground_window = ground_text[start_idx: start_idx + max_search_len]

    best_match = process.extractOne(ocr_text, [ground_window], scorer=fuzz.partial_ratio)
    if best_match:
        match_text, score, match_idx = best_match
        return match_text, start_idx + match_idx + len(match_text)
    return "", start_idx


def align_bboxes_with_true_text(listBBox, true_ground_text):

    list_pair_boxes = []
    current_index = 0

    for box in listBBox:
        ocr_text = box.get_clean_text()
        best_match, new_index = find_best_match_rapidfuzz(ocr_text, true_ground_text, current_index)
        list_pair_boxes.append((box, best_match))
        current_index = new_index
    

    return list_pair_boxes


def dump_aligned_boxes_to_json(aligned_pairs):
    enriched_boxes = []

    for bbox, true_text in aligned_pairs:
        enriched_box = {
            "page_name": bbox.,
            "id_page": "2",
            "id_box": idx + 1,  # Use idx+1 to start ID from 1
            "position": box["position"],
            "ocr_text": box["ocr_text"],
            "aligned_text": box["aligned_text"]
        }
        enriched_boxes.append(enriched_box)
    

    with open("output_text.json", 'w', encoding='utf-8') as json_file:
        json.dump(enriched_boxes, json_file, ensure_ascii=False, indent=4)



def main():
    # dir_name = "data"
    # os.makedirs(dir_name, exist_ok=True) 
    # print(f"Directory '{dir_name}' created successfully.")
    # crawl_text_from_web("./data/raw_text.txt")
    # clean_text(raw_text_path = "./data/raw_text.txt", clean_text_path="./data/clean_text.txt")



    with open("./data/clean_text.txt", 'r', encoding='utf-8') as cleanText:
        true_ground_text = cleanText.read()
    
    with open("page048_TayDuKy.json", "rb") as json_file:
        listBBox = BBoxes_of_JSON(json_file.read())




    for _bbox in listBBox:
        print(_bbox.get_position(), _bbox.get_text())

    aligned_boxes = align_bboxes_with_true_text(listBBox, true_ground_text)


    # for _align in aligned_boxes:
    #     print(_align)

    dump_aligned_boxes_to_json(aligned_boxes)

if __name__ == "__main__":
    main()