import pandas as pd
import os
from extract.bedrock_pdf_to_csv import extract_pdf_with_bedrock
from extract.process_statements import statement_to_df
from transform.normalise_data import normalise_df

parent_directory = "./statements"
 
all_data = []

def fetch_transactions(parent_directory):
    
    for card_folder in os.listdir(parent_directory):
        folder_path = os.path.join(parent_directory,card_folder)
        if not os.path.isdir(folder_path):
            continue

        for data_file in os.listdir(folder_path):
            file_path = os.path.join(folder_path,data_file)
            print(f"Processing {file_path}")
            
            df = statement_to_df(file_path)
            if df is not None and not df.empty:
                all_data.append(df)
        
        if all_data:
            card_df = pd.concat(all_data,ignore_index=True)
            
            card_df = normalise_df(card_df)
            card_df['card'] = card_folder
            
    return(card_df)
        

 