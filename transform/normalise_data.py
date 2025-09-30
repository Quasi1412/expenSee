import os
import pandas as pd
from io import StringIO
from pathlib import Path
from transform.categorise_with_ollama import categorise_transaction

def normalise_date(d):
    
    default_year = "2025" #Need to be fixed
    
    try: 
        return pd.to_datetime(d,errors='coerce')
    except Exception:
        return pd.to_datetime(f"{d} {default_year}")

def normalise_df(input_files, output_file):
    
    normal_df = []
    input_files_list = eval(input_files)
    
    for file in input_files_list:
        
        df = pd.read_csv(file)
        card_name = Path(file).stem
        
        df.columns = [col.strip().lower().replace(' ','_') for col in df.columns]
        
        date_col = next((col for col in df.columns if 'date' in col),None)
        description_col = next((col for col in df.columns if 'description' in col or 'details' in col))
        amount_col = next((col for col in df.columns if 'amount' in col or 'charges' in col or 'debit' in col))

        #Call the Ollama model to categorise the transaction if not already categorised
        if 'category' not in df.columns:
            df['category'] = df[description_col].apply(categorise_transaction)
        
        filtered_df = df[[date_col,description_col,'category',amount_col]]
        filtered_df.columns = ['transaction_date','description','category','amount']
        

        filtered_df['transaction_date'] = filtered_df['transaction_date'].apply(normalise_date)
        filtered_df['amount'] = pd.to_numeric(filtered_df['amount'].astype(str).str.replace(r"[^\d.-]","",regex=True),errors='coerce')
        filtered_df['card_name'] = card_name
        
        normal_df.append(filtered_df)
    
    final_df = pd.concat(normal_df, ignore_index=True)
    final_df.to_csv(output_file, index=False)
      
    return(output_file)
    


