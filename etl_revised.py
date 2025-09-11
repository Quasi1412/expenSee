import pandas as pd
import os
from bedrock_pdf_to_csv import extract_pdf_with_bedrock
from process_statements import statement_to_df

parent_directory = "./statements"
all_data = []


for card_folder in os.listdir(parent_directory):
    folder_path = os.path.join(parent_directory,card_folder)
    if not os.path.isdir(folder_path):
        continue

    for data_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path,data_file)
        df = statement_to_df(file_path)
        if not df.empty:
            all_data.append(df)
    
    if all_data:
        card_df = pd.concat(all_data,ignore_index=True)
        
        card_df['card'] = card_folder
        
        
            
        
        
    
        

 