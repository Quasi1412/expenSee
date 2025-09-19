import os
import shelve
import requests

LLM_API_URI = "http://host.docker.internal:11434/v1/chat/completions"
LLM_MODEL = "gemma3:12b"

cache_path = ".cache/cache.db"
os.makedirs(os.path.dirname(cache_path))

def categorise_transaction(description):
    
    description_key = description.strip().lower()
    category = None
    
    try:
        #Check for the description in cache 
        with shelve.open(cache_path) as cache:
            if description_key in cache:
                return cache[description_key]
        
            prompt = f"""You are a financial categorization assistant. Your task is to categorize the following credit card transaction 
                        into exactly one of these categories (return only one from this list):\n\n
                        Groceries, Restaurants, Travel, Gas, Public Transit, StreamingService, Insurance, Utilities, Entertainment, Internet, 
                        Healthcare, Education, Subscription, Shopping, Electronics, Fitness, Rent, Loan, CreditPayment, PetCare, 
                        AutoRepair, Fees, Gifts, Beauty, Coffee, Clothing, Taxes, Medical, Software, Shipping, Museum, OnlineShopping, Other\n\n
                        Respond with only **one** word from the list above, with no explanation or sentence.\n\n
                        Description: \"{description}\"
                        """
            
            payload = {
                "model":LLM_MODEL,
                "messages": [{"role":"user","content":prompt}],
                "temperature":0
            }
            
            #Run model when description not in cache
            response = requests.post(LLM_API_URI,json=payload,timeout=10)
            result = response.json()
            category = result["choices"][0]["message"]["content"]
            
            #Writing to description to cache memory 
            cache[description_key] = category
            
    except Exception as e:
        print(f"{LLM_MODEL} failed for {description} ")
        category = 'Uncategorised'  
        
    return category