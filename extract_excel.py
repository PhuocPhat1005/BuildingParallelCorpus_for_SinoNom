# @Contributors: Tu
# Purpose: Extract data from Excel files, sort them into Sentence and Paragraph
# Include: remove_punctuation(text), Sentence, Paragraph, extract_data(excel_path)

# Import libraries
import re
import pandas as pd

# Function to remove punctuation from text
def remove_punctuation(text):
    # Remove Chinese and English punctuation using regex
    return re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)

# Classes implementation
class Sentence:
    def __init__(self, original):
        self.original = original                          # Contains punctuations
        self.stripped = remove_punctuation(self.original) # No punctuations

class Paragraph:
    def __init__(self, number):
        self.number = number
        self.sentences = []

    def add_sentence(self, sentence):
        if isinstance(sentence, Sentence):
            self.sentences.append(sentence)

# Extract data from Excel files
def extract_data(excel_path):
    # Read Excel file
    df = pd.read_excel(excel_path, header=None, names=["Text"])
    df.dropna(inplace=True)
    paragraphs = []
    current_paragraph = None

    for index, row in df.iterrows():
        text = row["Text"]
        if text.startswith("Paragraph"):  # Detect paragraph headers
            # Create a new Paragraph object
            paragraph_number = int(text.split()[-1])
            current_paragraph = Paragraph(paragraph_number)
            paragraphs.append(current_paragraph)
        elif current_paragraph and isinstance(text, str):  # Add sentences to the current paragraph
            current_paragraph.add_sentence(Sentence(text.strip()))

    return paragraphs

if __name__ == "__main__":
    # File path to your Excel file
    file_path = "tqdn2_ch.xlsx"
    
    # Process the file and create Paragraph objects
    paragraphs = extract_data(file_path)
    
    # Display the results
    for paragraph in paragraphs:
        print(f"Paragraph {paragraph.number}:")
        for sentence in paragraph.sentences:
            print(f"  Original: {sentence.original}")
            print(f"  Stripped: {sentence.stripped}")