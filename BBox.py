# @Contributors: $VoThinhVuong$

import json
import re


class Words:
    def __init__(self,box_word) -> None:
        self._text = box_word["text"]
        # self._choices = box_word["choices"]
        self._det_confidence = box_word["det_confidence"]
        self._confidence = box_word["det_confidence"]
        self._position = box_word["position"]
    
    @property
    def text(self):
        return self._text

    @property
    def confidence(self):
        return self._confidence

    @property
    def det_confidence(self):
        return self._det_confidence
    
    @property
    def position(self):
        return self._position
    
    def __repr__(self):
        return (f"Word(text={self._text}, confidence={self._confidence}, "f"det_confidence={self._det_confidence}, position={self._position})")

class BBox:
    def __init__(self, box, page_name, id_page, id_box) -> None:
        self._base_text = box["text"]
        self._cleaned_text = re.sub(r'[^\u4E00-\u9FFF\u3400-\u4DBF\u2000-\u2A6D\u2A70-\u2EBE\uF900-\uFAFF]', '', box["text"])
        self._position = box["position"]
        self._words = [ Words(box_word) for box_word in box["words"] if box_word["text"] in self._cleaned_text ]
        self._page_name = page_name
        # self._id_page = f".{id_page}"
        # self._id_box = f".0{id_box}" if id_box < 10 else f".{id_box}"
        self._id_page = id_page
        self._id_box = id_box

    def get_position(self):
        return self._position
    
    def get_cleaned_text(self):
        return self._cleaned_text
    
    def get_base_text(self):
        return self._base_text

    def get_words(self):
        return self._words
    
    def get_length(self):
        return len(self._cleaned_text_text)
    
    def get_id_box(self):
        return self._id_box
    
    def get_id_page(self):
        return self._id_page
    
    def get_page_name(self):
        return self._page_name

    def get_height(self):
        return self._position[3][1] - self._position[0][1]

    def __repr__(self):
        return (f"BBox(position={self._position}, base_text={self._base_text}, cleaned_text ={self._cleaned_text},"
                f"page_name={self._page_name}, id_page={self._id_page}, id_box={self._id_box} ,words={self._words}),")
        

# JSON phải có các giá trì từ return_position và return_choices của API
def BBoxes_of_JSON(json_file, file_name):
    try:
        data = json.loads(json_file)
    except ValueError:
        print("Không xử lý được file json.")
        return
    
    page_name = file_name[:7]
    id_page = int(file_name[-8:-5])

    result = []
    i = 1
    for idx, text_line in enumerate(data["data"]["text_lines"]):
        temp = BBox(text_line,page_name,id_page, i)
        # print(temp.get_height())
        # if temp.get_height() >= 65:
        result.append(temp)
        i += 1

    return result






#testing
def main():
    res = []
    file_name = "TayDuKy_page048.json"
    with open(file_name, "rb") as json_file:
        res = BBoxes_of_JSON(json_file.read(), file_name)

    for _sentence in res:
        print(_sentence.get_base_text())
        print(_sentence.get_cleaned_text())
        print(_sentence.get_position())
        print(_sentence.get_height())
        print(_sentence.get_page_name())
        print(_sentence.get_id_page())
        print(_sentence.get_id_box())
        print("=====================")



if __name__ == "__main__":
    main()


