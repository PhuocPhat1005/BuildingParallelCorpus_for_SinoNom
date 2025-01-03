from extract_text_from_web import crawl_text_from_web, clean_text
from extract_pdf import extract_images
from extract_multiple import get_json
from align_boxes import align_bboxes_with_true_text, dump_aligned_boxes_to_csv, dump_aligned_boxes_to_json
from alignment_process import DictionaryLoader, TextAlignment
from write_output import load_alignment_results, ExcelExporterProcessing
from BBox import BBox, BBoxes_of_JSON, remove_trash_boxes_by_height
from rename import rename_json
import os, re


def main():

    pdf_path = "ThuyHu.pdf"

    # Folder chứa data bản txt (trước khi xử lý)
    folder_raw_txt = r"./data/raw_text.txt"





    # Mặc định thư mục chứa data
    dir_name = "data"
    pdf_name = pdf_path[:-4]
    img_dir = r"assets\images"
    aligned_text_json = "output_text.json"

    folder_json = r'assets\json'

    # Chỉ định Folder chứa data bản txt (sau khi xử lý)
    folder_clean_txt = r"./data/clean_text.txt"

    # Ngưỡng để check bounding box
    _threshhold = 5



    # Get ground text from web
    # os.makedirs(dir_name, exist_ok=True) 
    # print(f"Tạo thư mục '{dir_name}' thành công.")
    # # crawl_text_from_web(folder_raw_txt)
    clean_text(raw_text_path =folder_raw_txt , clean_text_path=folder_clean_txt)

    # Get images from pdf
    print("Thực hiện trích xuất hình ảnh... (1.5 giây/1 trang)")

    # IMPORTANT!!!!!!: add a 3rd parameter for number of pages to extract if necessary, default is all pages 
    extract_images(pdf_path, img_dir, num_of_pages=300, start_page=600)

    print("Trích xuất ảnh thành công!")

    # Get OCR results
    print("Thực hiện OCR hình ảnh... (1.5 giây/1 ảnh)")
    get_json(img_dir, folder_json)


    #Align OCR strings with Ground strings
    print("Thực hiện dóng hàng chuỗi OCR với chuỗi chuẩn...")
    with open(folder_clean_txt, 'r', encoding='utf-8') as cleanText:
        true_ground_text = cleanText.read()

    listBBox = []
    directory = 'assets/json/'
    pattern = r'^' + pdf_name + r'_page' + r'\d{3}\.json$'
    for filename in os.listdir(directory):
        if re.match(pattern, filename):
            full_file_path = os.path.join(directory, filename)
            with open(full_file_path, "rb") as json_file:
                listBBox += BBoxes_of_JSON(json_file.read(), filename)
    print(len(listBBox))


    listBBox = remove_trash_boxes_by_height(listBBox,_threshhold)

    print(len(listBBox))

    aligned_boxes = align_bboxes_with_true_text(listBBox, true_ground_text)

    dump_aligned_boxes_to_json(aligned_boxes, output_text_json=aligned_text_json)

    align_text_csv = "ocr_corrections.csv"
    dump_aligned_boxes_to_csv(aligned_boxes, align_text_csv)

    print("Dóng hàng thành công!")

    # Align characters
    print("Thực hiện dóng hàng các ký tự...")
    alignment_bbox_results = load_alignment_results(aligned_text_json)

    sinonom_dict_filename = "SinoNom_similar_Dic.xlsx"
    dictionaries = DictionaryLoader(sinonom_dict_filename)
    sinonom_dict = dictionaries.load_dictionaries()

    text_alignment_processor = TextAlignment(sinonom_dict, alignment_bbox_results)
    char_alignment_results = text_alignment_processor.calculate_alignment()

    print("Dóng hàng thành công!")

    # Output results to Excel
    json_file_path = "align_text.json"
    alignment_results = load_alignment_results(json_file_path)

    output_file_path = "output.xlsx"

    excel_exporter = ExcelExporterProcessing(output_file_path, alignment_results)
    excel_exporter.setup_headers()
    excel_exporter.generate_output_excel()
    excel_exporter.close()

    print(f"Kết quả đã được lưu vào {output_file_path}")

if __name__ == "__main__":
    main()