# Contributors: Lê Phước Phát

import pandas as pd

file_path = 'output_test.xlsx'

df = pd.read_excel(file_path, engine='openpyxl')

extracted_columns = df[['Text OCR', 'Text Char']]

output_csv_path = 'extracted_csv.csv'

extracted_columns.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

output_csv_path