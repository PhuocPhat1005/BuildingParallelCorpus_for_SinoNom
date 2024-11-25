# @Contributors: $VoThinhVuong$

import json


class Words:
    def __init__(self,box_word) -> None:
        self._text = box_word["text"]
        self._choices = box_word["choices"]
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
    def __init__(self, box) -> None:
        self._text = box["text"]
        self._position = box["position"]
        self._words = [ Words(box_word) for box_word in box["words"] ]


    @property
    def position(self):
        return self._position

    @property
    def text(self):
        return self._text

    @property
    def words(self):
        return self._words
    
    def length(self):
        return len(self._text)

    def __repr__(self):
        return (f"BBox(position={self._position}, text={self._text}, "
                f"words={self._words})")
        

# JSON phải có các giá trì từ return_position và return_choices của API
def BBoxes_of_JSON(json_file):
    try:
        data = json.loads(json_file)
    except ValueError:
        print("Không xử lý được file json.")
        return
    
    return [ BBox(text_line) for text_line in data["data"]["text_lines"] ]

#testing
# with open("response.json", "rb") as json_file:
#     res = BBoxes_of_JSON(json_file.read())
#     print(res[0])
