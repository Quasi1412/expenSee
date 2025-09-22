from sqlalchemy import create_engine
import pandas as pd
import os

PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE')
PG_URL = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}'

def push_data_to_db(transaction_df):
    
    engine = create_engine(PG_URL)
    
    #Get schema from df
    transaction_df.head(0).to_sql("expenses", con=engine, if_exists='replace', index=False)
    print("Table has been created!!")
    
    print(f"Inserting {transaction_df['card_name'].unique()} data into {PG_DATABASE}")
    transaction_df.to_sql("expenses",con=engine, if_exists='append', index=False)
    
    print(f"{transaction_df['card_name'].unique()} has been inserted ✅") 