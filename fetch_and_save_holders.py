import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import os

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

# Read or initialize progression data
if os.path.exists('progression_data.csv'):
    progression_df = pd.read_csv('progression_data.csv')
else:
    progression_df = pd.DataFrame(columns=['timestamp', 'total_holders', 'holders_gt_11', 'holders_gt_111'])

# Add the current data
current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
total_holders = df.shape[0]
holders_gt_11 = df[df['Balance'] > 11].shape[0]
holders_gt_111 = df[df['Balance'] > 111].shape[0]
new_row = {
    'timestamp': current_time,
    'total_holders': total_holders,
    'holders_gt_11': holders_gt_11,
    'holders_gt_111': holders_gt_111
}
progression_df = progression_df.append(new_row, ignore_index=True)

# Save the progression data
progression_df.to_csv('progression_data.csv', index=False)

# Plot the progression curve
plt.figure(figsize=(10, 6))
plt.plot(progression_df['timestamp'], progression_df['total_holders'], label='All Holders', color='black')
plt.plot(progression_df['timestamp'], progression_df['holders_gt_11'], label='Holders >11', color='red')
plt.plot(progression_df['timestamp'], progression_df['holders_gt_111'], label='Holders >111', color='blue')
plt.xlabel('Time')
plt.ylabel('Number of Holders')
plt.title('Progression Curve')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('progression_curve.png')

# Update the README.md
with open('README.md', 'w') as readme_file:
    readme_file.write(f"# Zora Token Holders\n\n")
    readme_file.write(f"## Last updated: {current_time}\n\n")
    readme_file.write(f"Total holders: {total_holders}\n\n")
    readme_file.write(f"## Holders Data\n")
    readme_file.write(df.to_markdown())

print("Data fetching and saving completed. Saved to data.csv, progression_data.csv, and README.md updated.")
