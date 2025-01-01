# @Contributors: Thai

from bs4 import BeautifulSoup
import requests
import os
from BBox import clean_text


# These lines are used to crawl all the text of "TayDuKy"


URL_WEBSITE = "https://www.gutenberg.org/cache/epub/23962/pg23962-images.html"



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
    _clean_text = clean_text(''.join(raw_text.split()).replace('\t', '').replace('\n', '').strip())

    with open(clean_text_path, "w", encoding='utf-8') as file:
        file.write(_clean_text)

def main():
    dir_name = "data"
    os.makedirs(dir_name, exist_ok=True) 
    print(f"Directory '{dir_name}' created successfully.")
    crawl_text_from_web("./data/raw_text.txt")
    clean_text(raw_text_path = "./data/raw_text.txt", clean_text_path="./data/clean_text.txt")


if __name__ == "__main__":
    main()
