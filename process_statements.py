from io import StringIO
import pandas as pd

from bedrock_pdf_to_csv import extract_pdf_with_bedrock

def statement_to_df(file_path):
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            return df
        
        elif file_path.endswith('.pdf'):
            
            extracted_table = extract_pdf_with_bedrock(file_path)
            
            #Removing the ```csv fences and white spaces if available
            if extracted_table.startswith("```csv"):
                extracted_table = extracted_table[6:]
                if extracted_table.endswith("```"):
                    extracted_table = extracted_table[:-3]
            extracted_table = extracted_table.strip()
                
            df = pd.read_csv(StringIO(extracted_table))
            
            return df
        
        else:
            raise ValueError(f'Unsupported File format: {file_path}')
    
    except Exception as e:
        print(f"Error Processing {file_path}. Response: {e}")
        return None