import requests
import pandas as pd
import datetime

# API base URL for the first page
base_url = "https://explorer.zora.energy/api/v2/tokens/0x7777777d57c1C6e472fa379b7b3B6c6ba3835073/holders"

# Initialize an empty list to store the data
holders_data = []

# Function to fetch data
def fetch_data(url):
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

# Fetch the first page
data = fetch_data(base_url)
if data and 'items' in data:
    items = data.get('items', [])
    holders_data.extend([[item['address']['hash'], item['value']] for item in items])

    # Handle pagination using next_page_params
    while 'next_page_params' in data:
        next_page_params = data['next_page_params']
        if next_page_params:
            address_hash = next_page_params.get('address_hash')
            items_count = next_page_params.get('items_count')
            value = next_page_params.get('value')
            next_page_url = f"{base_url}?address_hash={address_hash}&items_count={items_count}&value={value}"
            data = fetch_data(next_page_url)
            if data and 'items' in data:
                items = data.get('items', [])
                holders_data.extend([[item['address']['hash'], item['value']] for item in items])
                print(f"Fetched page with params: {next_page_params}")
            else:
                break
        else:
            break

# Convert the list to a DataFrame
df = pd.DataFrame(holders_data, columns=['HolderAddress', 'Balance'])

# Save the DataFrame to a CSV file
df.to_csv('data.csv', index=False)

# Update the README.md
current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
with open('README.md', 'w') as readme_file:
    readme_file.write(f"# Zora Token Holders\n\n")
    readme_file.write(f"## Last updated: {current_time}\n\n")
    readme_file.write(f"Total holders: {df.shape[0]}\n\n")
    readme_file.write(f"## Holders Data\n")
    readme_file.write(df.to_markdown())

print("Data fetching and saving completed. Saved to data.csv and README.md updated.")
