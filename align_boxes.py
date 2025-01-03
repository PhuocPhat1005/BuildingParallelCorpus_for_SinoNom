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


# def find_best_match_rapidfuzz(ocr_text, ground_text, start_idx):
#     best_match_text = ""
#     best_match_score = 0
#     best_match_idx = 0
#     score = 0
#     i = 0
#     hanzi_ocr_text = convert_hanzi_strings(ocr_text)
#     hanzi_ground_text = convert_hanzi_strings(ground_text)
#     while i < len(ground_text):
#         candidate = hanzi_ground_text[i:i + len(hanzi_ocr_text)]
#         score = calculate_match_score(hanzi_ocr_text, candidate)  # RapidFuzz ratio: 0 đến 1

#         if score > best_match_score:
#             best_match_text = candidate
#             best_match_score = score
#             best_match_idx = i
        
#         i += 1
#     if best_match_score > 0.35:
#         pos1, pos2 = align_strings(hanzi_ocr_text, best_match_text)
#         if pos1 == None or pos2 == None:
#             return "", start_idx
#         number_of_redundant_char = 0
#         new_pos_best_match_text = pos2 + number_of_redundant_char
#         cut_best_match_text = ground_text[best_match_idx:best_match_idx+new_pos_best_match_text + 1]
#         new_pos_best_match_text = best_match_idx+pos2 + number_of_redundant_char
#         return cut_best_match_text, start_idx + new_pos_best_match_text + 1
#     return "", start_idx



from rapidfuzz import fuzz

# def find_best_match_rapidfuzz(ocr_text, ground_text, start_idx):
#     """
#     Find the best match of ocr_text in ground_text using RapidFuzz.

#     Args:
#         ocr_text (str): Text from OCR.
#         ground_text (str): Ground truth text.
#         start_idx (int): Starting index in the ground_text.

#     Returns:
#         tuple: (best_match_text, best_match_end_idx)
#     """
#     hanzi_ocr_text = convert_hanzi_strings(ocr_text)
#     hanzi_ground_text = convert_hanzi_strings(ground_text)
#     best_match_text = ""
#     best_match_score = 0
#     best_match_idx = -1

#     # Sử dụng RapidFuzz để tìm match tốt nhất
#     for i in range(len(hanzi_ground_text) - len(hanzi_ocr_text) + 1):
#         candidate = hanzi_ground_text[i:i + len(hanzi_ocr_text)]
#         score = fuzz.ratio(hanzi_ocr_text, candidate) / 100  # RapidFuzz ratio từ 0 đến 1

#         if score > best_match_score:
#             best_match_text = candidate
#             best_match_score = score
#             best_match_idx = i

#     if best_match_score > 0.65 and best_match_idx != -1:
#         pos1, pos2 = align_strings(hanzi_ocr_text, best_match_text)
#         if pos1 is None or pos2 is None:
#             return "", start_idx
#         number_of_redundant_char = 0
#         new_pos_best_match_text = pos2 + number_of_redundant_char
#         # Tính vị trí kết thúc của match trong toàn bộ ground_text
#         best_match_end_idx = start_idx + best_match_idx + new_pos_best_match_text + 1
#         return best_match_text, best_match_end_idx
#     else:
#         return "", 0


def find_best_match_rapidfuzz(ocr_text, ground_text, start_idx):
    """
    Find the best match of ocr_text in ground_text using RapidFuzz.

    Args:
        ocr_text (str): Text from OCR.
        ground_text (str): Ground truth text.
        start_idx (int): Starting index in the ground_text.

    Returns:
        tuple: (best_match_text, best_match_end_idx)
    """
    # Chuyển đổi chỉ ocr_text
    converted_ocr_text = convert_hanzi_strings(ocr_text)
    
    best_match_text = ""
    best_match_score = 0
    best_match_idx = -1

    # Lặp qua từng vị trí có thể trong ground_text
    for i in range(len(ground_text) - len(ocr_text) + 1):
        candidate_original = ground_text[i:i + len(ocr_text)]
        converted_candidate = convert_hanzi_strings(candidate_original)
        score = fuzz.ratio(converted_ocr_text, converted_candidate) / 100  # RapidFuzz ratio từ 0 đến 1

        if score > best_match_score:
            best_match_text = candidate_original  # Lấy từ ground_text gốc
            best_match_score = score
            best_match_idx = i

    if best_match_score > 0.75 and best_match_idx != -1:
        # Sử dụng convert_hanzi_strings cho best_match_text để align
        pos1, pos2 = align_strings(converted_ocr_text, convert_hanzi_strings(best_match_text))
        if pos1 is None or pos2 is None:
            return "", start_idx
        number_of_redundant_char = 0
        new_pos_best_match_text = pos2 + number_of_redundant_char
        # Tính vị trí kết thúc của match trong toàn bộ ground_text
        best_match_end_idx = start_idx + best_match_idx + new_pos_best_match_text + 1
        return best_match_text, best_match_end_idx
    else:
        return "", 0








# def align_bboxes_with_true_text(listBBox, true_ground_text):

#     list_pair_boxes = []
#     current_index = 0
#     for box in listBBox:
#         ocr_text = box.get_cleaned_text()
#         if len(ocr_text) < 15:
#             max_search_len = len(ocr_text) + 50
#         else:
#             max_search_len = len(ocr_text) + 250
#         ground_text = true_ground_text[current_index:current_index+max_search_len]
#         best_match, new_index = find_best_match_rapidfuzz(ocr_text, ground_text, current_index)
#         list_pair_boxes.append((box, best_match))
#         current_index = new_index

#     return list_pair_boxes


def align_bboxes_with_true_text(listBBox, true_ground_text):
    """
    Align bounding boxes with the corresponding true ground text.

    Args:
        listBBox (list): List of bounding box objects with OCR text.
        true_ground_text (str): The ground truth text to align with.

    Returns:
        list: A list of tuples where each tuple contains a bounding box and its matched text.
    """
    list_pair_boxes = []
    current_index = 0
    total_length = len(true_ground_text)

    for idx, box in enumerate(listBBox):
        ocr_text = box.get_cleaned_text()
        ocr_length = len(ocr_text)

        # Determine max_search_len based on the length of ocr_text
        if ocr_length < 15:
            max_search_len = ocr_length + 50
        else:
            max_search_len = ocr_length + 250

        print(f"Processing bbox {idx +1}/{len(listBBox)}: OCR text length {ocr_length}, max_search_len {max_search_len}")

        if idx == 0:
            # **Đối với bbox đầu tiên:**
            # Tìm kiếm trên toàn bộ true_ground_text
            ground_text = true_ground_text
            print(f"  First bbox: Searching entire ground_text")
            best_match, new_index = find_best_match_rapidfuzz(ocr_text, ground_text, 0)

            if best_match:
                list_pair_boxes.append((box, best_match))
                current_index = new_index
                print(f"    Match found: '{best_match}' at index {new_index}")
            else:
                # Nếu không tìm thấy match, ghép với chuỗi rỗng
                list_pair_boxes.append((box, ""))
                print(f"    No match found for first bbox.")
        else:
            # **Đối với các bbox tiếp theo:**
            match_found = False
            temp_index = current_index  # Sử dụng biến tạm để không thay đổi current_index ngay lập tức
            start_index = current_index


            while not match_found and temp_index < total_length:
                # Xác định phạm vi tìm kiếm hiện tại
                search_end = temp_index + max_search_len
                ground_text = true_ground_text[temp_index:search_end]
                print(f"  Subsequent bbox: Searching ground_text[{temp_index}:{search_end}]")
                best_match, new_index = find_best_match_rapidfuzz(ocr_text, ground_text, temp_index)
                print(f"    Best match: '{best_match}', new_index: {new_index}")

                if best_match:
                    if new_index != 0:
                        # Nếu tìm thấy match và new_index khác temp_index
                        list_pair_boxes.append((box, best_match))
                        current_index = new_index
                        match_found = True
                        print(f"      Match found: '{best_match}' at index {new_index}")
                    else:
                        # Nếu new_index == 0, tăng temp_index lên max_search_len và thử lại
                        print(f"      new_index == temp_index. Incrementing temp_index by max_search_len.")
                        temp_index += max_search_len
                else:
                    # Nếu không tìm thấy match trong phạm vi hiện tại, tăng temp_index và thử lại
                    print(f"    No match found in current window. Incrementing temp_index by max_search_len.")
                    temp_index += max_search_len

            if not match_found:
                # Nếu sau khi tăng temp_index mà vẫn không tìm thấy match
                list_pair_boxes.append((box, ""))
                print(f"    No match found for bbox {idx +1}.")
                # Cập nhật current_index để tránh vòng lặp vô hạn nếu cần thiết
                current_index = min(start_index, total_length)

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
