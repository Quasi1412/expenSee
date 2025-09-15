import pandas as pd
from io import StringIO

def normalise_df(df):
    
    df.columns = [col.strip().lower().replace(' ','_') for col in df.columns]
    
    date_col = next((col for col in df.columns if 'date' in col),None)
    description_col = next((col for col in df.columns if 'description' in col or 'details' in col))
    amount_col = next((col for col in df.columns if 'amount' in col or 'charges' in col or 'debit' in col))
    
    #Assuming default year, need to fix in future
    year_default = 2025
    
    filtered_df = df[[date_col,description_col,amount_col]]
    filtered_df.columns = ['transaction_date','description','amount']
    
    filtered_df['transaction_date'] = filtered_df['transaction_date'].apply(lambda d: pd.to_datetime(f"{d}/{year_default}",format="%m/%d/%Y"))
    filtered_df['amount'] = pd.to_numeric(filtered_df['amount'].astype(str).str.replace(r"[^\d.-]","",regex=True),errors='coerce')
    
    return(filtered_df)
    


