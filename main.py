from extract_text_from_web import crawl_text_from_web, clean_text
from extract_pdf import extract_images
from extract_multiple import get_json
from align_boxes import align_bboxes_with_true_text, dump_aligned_boxes_to_csv, dump_aligned_boxes_to_json
from alignment_process import DictionaryLoader, TextAlignment
from write_output import load_alignment_results, ExcelExporterProcessing
from BBox import BBox, BBoxes_of_JSON
import os, re


def main():
    # Directories
    dir_name = "data"
    pdf_path = "TayDuKy.pdf"
    img_dir = r"assets\images"
    aligned_text_json = "output_text.json"

    # Get ground text from web
    os.makedirs(dir_name, exist_ok=True) 
    print(f"Directory '{dir_name}' created successfully.")
    crawl_text_from_web("./data/raw_text.txt")
    clean_text(raw_text_path = "./data/raw_text.txt", clean_text_path="./data/clean_text.txt")

    # Get images from pdf
    print("Extracting images... (1.5 seconds/1 page)")
    extract_images(pdf_path, img_dir)
    print("Images extracted successfully!")

    # Get OCR results
    get_json(img_dir, r"assets\json")

    #Align OCR strings with Ground strings
    print("Aligning OCR strings with Ground strings...")
    with open("./data/clean_text.txt", 'r', encoding='utf-8') as cleanText:
        true_ground_text = cleanText.read()

    listBBox = []
    directory = 'assets/json/'
    pattern = r'^TayDuKy_page\d{3}\.json$'
    for filename in os.listdir(directory):
        if re.match(pattern, filename):
            full_file_path = os.path.join(directory, filename)
            with open(full_file_path, "rb") as json_file:
                listBBox += BBoxes_of_JSON(json_file.read(), filename)

    aligned_boxes = align_bboxes_with_true_text(listBBox, true_ground_text)

    dump_aligned_boxes_to_json(aligned_boxes, output_text_json=aligned_text_json)

    align_text_csv = "ocr_corrections.csv"
    dump_aligned_boxes_to_csv(aligned_boxes, align_text_csv)

    print("Finished aligning strings!")

    # Align characters
    print("Aligning characters...")
    alignment_bbox_results = load_alignment_results(aligned_text_json)

    sinonom_dict_filename = "SinoNom_similar_Dic.xlsx"
    dictionaries = DictionaryLoader(sinonom_dict_filename)
    sinonom_dict = dictionaries.load_dictionaries()

    text_alignment_processor = TextAlignment(sinonom_dict, alignment_bbox_results)
    char_alignment_results = text_alignment_processor.calculate_alignment()

    print("Finished aligning characters!")

    # Output results to Excel
    json_file_path = "align_text.json"
    alignment_results = load_alignment_results(json_file_path)

    output_file_path = "output.xlsx"

    excel_exporter = ExcelExporterProcessing(output_file_path, alignment_results)
    excel_exporter.setup_headers()
    excel_exporter.generate_output_excel()
    excel_exporter.close()

    print(f"Results save to {output_file_path}")

if __name__ == "__main__":
    main()