from sqlalchemy import create_engine
import pandas as pd
import os



def push_data_to_db(transaction_df, PG_URL):
    
    engine = create_engine(PG_URL)
    
    #Get schema from df
    transaction_df.head(0).to_sql("expenses", con=engine, if_exists='replace', index=False)
    print("Table has been created!!")
    
    print(f"Inserting {transaction_df['card_name'].unique()} data into {PG_DATABASE}")
    transaction_df.to_sql("expenses",con=engine, if_exists='append', index=False)
    
    print(f"{transaction_df['card_name'].unique()} has been inserted ✅") 