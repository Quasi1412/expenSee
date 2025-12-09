from io import StringIO
import pandas as pd

#from extract.bedrock_pdf_to_csv import extract_pdf_with_bedrock
from extract_with_textract import extract_table_with_textract

def statement_to_df(file_path):
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            return df
        
        elif file_path.endswith('.pdf'):
            
            df = extract_table_with_textract(file_path)
            return df
        
        else:
            raise ValueError(f'Unsupported File format: {file_path}')
    
    except Exception as e:
        print(f"Error Processing {file_path}. Response: {e}")
        return None