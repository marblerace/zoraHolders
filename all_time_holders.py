import requests
import pandas as pd
import os

# API base URL for the first page
base_url = "https://explorer.zora.energy/api/v2/tokens/0x7777777d57c1C6e472fa379b7b3B6c6ba3835073/transfers"

# Initialize an empty set to store unique addresses
unique_addresses = set()

# Function to fetch data
def fetch_data(url):
    try:
        response = requests.get(url, headers={'accept': 'application/json'})
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

try:
    # Fetch the first page
    data = fetch_data(base_url)
    page_number = 1
    while data:
        if 'items' in data:
            items = data.get('items', [])
            for item in items:
                from_address = item['from']['hash']
                if from_address not in unique_addresses:
                    unique_addresses.add(from_address)
            print(f"Page {page_number}: Fetched {len(items)} transactions, {len(unique_addresses)} unique addresses found.")
        
        if 'next_page_params' in data:
            next_page_params = data['next_page_params']
            if next_page_params:
                block_number = next_page_params.get('block_number')
                index = next_page_params.get('index')
                next_page_url = f"{base_url}?block_number={block_number}&index={index}"
                data = fetch_data(next_page_url)
                if data is None:
                    print("Stopping further data fetching due to error.")
                    break
                page_number += 1
            else:
                print("No more pages to fetch.")
                break
        else:
            print("No more pages to fetch.")
            break

    # Convert the set to a DataFrame
    if data is not None:
        df = pd.DataFrame(list(unique_addresses), columns=['HolderAddress'])

        # Save the DataFrame to a CSV file
        df.to_csv('holders.csv', index=False)
        print("Data fetching and saving completed. Saved to holders.csv.")
    else:
        print("Data fetching halted due to server error; holders.csv not updated.")

except Exception as e:
    print(f"An error occurred: {e}")