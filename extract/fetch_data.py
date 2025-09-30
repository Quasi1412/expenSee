import pandas as pd
import os
from extract.process_statements import statement_to_df


def fetch_transactions(parent_directory, output_dir):
    os.makedirs(output_dir,exist_ok=True)
    
    all_csv = []
    
    for card_folder in os.listdir(parent_directory):
        folder_path = os.path.join(parent_directory,card_folder)
        if not os.path.isdir(folder_path):
            continue
        
        all_data = []
        for data_file in os.listdir(folder_path):
            file_path = os.path.join(folder_path,data_file)
            print(f"Processing {file_path}")
            
            df = statement_to_df(file_path)
            if df is not None and not df.empty:
                all_data.append(df)
        
        if all_data:
            card_df = pd.concat(all_data,ignore_index=True)
            output_file = os.path.join(output_dir,f'{card_folder}.csv')
            card_df.to_csv(output_file, index=False)
            all_csv.append(output_file)

    return(all_csv)
        

 