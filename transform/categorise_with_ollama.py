import os
import shelve
import requests
import re

LLM_API_URI = "http://localhost:11434/v1/chat/completions"
LLM_MODEL = "gemma3:12b"

cache_path = ".cache/cache.db"
os.makedirs(os.path.dirname(cache_path),exist_ok=True)

#Simple logic to normalise descritpion for efficient cache(Needs Improvement)
def normalise_cache(desc):
    
    us_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    }
    
    desc = desc.strip().upper()
    desc = re.sub(r"\d+","",desc)
    desc = re.sub(r"[^\w\s]","",desc)
    desc = re.sub(r"\s{2}"," ",desc)
    
    words = desc.split()
    
    words_no_state = [w for w in words if w not in us_states]
    
    normalised_desc = " ".join(words_no_state[:3])
    
    
    return normalised_desc

def categorise_transaction(description):
    
    description_key = normalise_cache(description)
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
            cache[description_key.strip()] = category
            
    except Exception as e:
        
        print(f"{LLM_MODEL} failed for {description} ")
        print(f"Reason: {e}")
        
        category = 'Uncategorised'  
        
    return category