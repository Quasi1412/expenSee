import pandas as pd
from io import StringIO
from transform.categorise_with_ollama import categorise_transaction

def normalise_date(d):
    
    default_year = "2025" #Need to be fixed
    
    try: 
        return pd.to_datetime(d,errors='coerce')
    except Exception:
        return pd.to_datetime(f"{d} {default_year}")

def normalise_df(df):
    
    df.columns = [col.strip().lower().replace(' ','_') for col in df.columns]
    
    date_col = next((col for col in df.columns if 'date' in col),None)
    description_col = next((col for col in df.columns if 'description' in col or 'details' in col))
    amount_col = next((col for col in df.columns if 'amount' in col or 'charges' in col or 'debit' in col))

    #Call the Ollama model to categorise the transaction if not already categorised
    if 'category' not in df.columns:
        df['category'] = df[description_col].apply(categorise_transaction)
        
    category_col = next(col for col in df.columns if 'category' in col)
      
    filtered_df = df[[date_col,description_col,category_col,amount_col]]
    filtered_df.columns = ['transaction_date','description','category','amount']
    

    filtered_df['transaction_date'] = filtered_df['transaction_date'].apply(normalise_date)
    filtered_df['amount'] = pd.to_numeric(filtered_df['amount'].astype(str).str.replace(r"[^\d.-]","",regex=True),errors='coerce')
    
    return(filtered_df)
    


