import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import os
import traceback

# API base URL for the first page
base_url = "https://explorer.zora.energy/api/v2/tokens/0x7777777d57c1C6e472fa379b7b3B6c6ba3835073/holders"

# Initialize an empty list to store the data
holders_data = []

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
                    print("No more data found or failed to fetch data.")
                    break
            else:
                print("No more pages to fetch.")
                break

    # Convert the list to a DataFrame
    df = pd.DataFrame(holders_data, columns=['HolderAddress', 'Balance'])

    # Ensure the 'Balance' column is converted to integers
    df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce').fillna(0).astype(int)

    # Save the DataFrame to a CSV file
    df.to_csv('data.csv', index=False)

    # Read or initialize progression data
    progression_file = 'progression_data.csv'
    if os.path.exists(progression_file):
        progression_df = pd.read_csv(progression_file)
    else:
        progression_df = pd.DataFrame(columns=['timestamp', 'total_holders', 'holders_gt_11', 'holders_gt_111'])

    # Add the current data
    current_time = datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M')  # European format without seconds and "UTC"
    total_holders = df.shape[0]
    holders_gt_11 = df[df['Balance'] > 11].shape[0]
    holders_gt_111 = df[df['Balance'] > 111].shape[0]
    new_row = pd.DataFrame({
        'timestamp': [current_time],
        'total_holders': [total_holders],
        'holders_gt_11': [holders_gt_11],
        'holders_gt_111': [holders_gt_111]
    })
    progression_df = pd.concat([progression_df, new_row], ignore_index=True)

    # Save the progression data
    progression_df.to_csv(progression_file, index=False)
    print("Progression data saved successfully.")

    # Plot the progression curves
    try:
        # Plot for all holders
        plt.figure(figsize=(10, 6))
        plt.plot(progression_df['timestamp'], progression_df['total_holders'], label='All Holders', color='black')
        plt.xlabel('Time')
        plt.ylabel('Number of Holders')
        plt.title('Progression Curve - All Holders')
        plt.xticks(rotation=45)
        plt.yticks(range(0, max(progression_df['total_holders']) + 1))
        plt.tight_layout()
        plt.savefig('progression_curve_all.png')
        plt.close()

        # Plot for holders > 11
        plt.figure(figsize=(10, 6))
        plt.plot(progression_df['timestamp'], progression_df['holders_gt_11'], label='Holders >11', color='red')
        plt.xlabel('Time')
        plt.ylabel('Number of Holders')
        plt.title('Progression Curve - Holders >11')
        plt.xticks(rotation=45)
        plt.yticks(range(0, max(progression_df['holders_gt_11']) + 1))
        plt.tight_layout()
        plt.savefig('progression_curve_gt_11.png')
        plt.close()

        # Plot for holders > 111
        plt.figure(figsize=(10, 6))
        plt.plot(progression_df['timestamp'], progression_df['holders_gt_111'], label='Holders >111', color='blue')
        plt.xlabel('Time')
        plt.ylabel('Number of Holders')
        plt.title('Progression Curve - Holders >111')
        plt.xticks(rotation=45)
        plt.yticks(range(0, max(progression_df['holders_gt_111']) + 1))
        plt.tight_layout()
        plt.savefig('progression_curve_gt_111.png')
        plt.close()

        print("Progression curve graphs saved successfully.")
    except Exception as e:
        print(f"Failed to plot and save progression curve graphs: {e}")
        traceback.print_exc()

    # Check if progression_curve.png exists
    if os.path.exists('progression_curve_all.png'):
        print("Progression curve graph for all holders exists.")
    else:
        print("Progression curve graph for all holders does not exist.")

    if os.path.exists('progression_curve_gt_11.png'):
        print("Progression curve graph for holders >11 exists.")
    else:
        print("Progression curve graph for holders >11 does not exist.")

    if os.path.exists('progression_curve_gt_111.png'):
        print("Progression curve graph for holders >111 exists.")
    else:
        print("Progression curve graph for holders >111 does not exist.")

    # Update the README.md
    try:
        previous_df = None
        if os.path.exists('previous_results.txt'):
            previous_df = pd.read_csv('previous_results.txt')

        mean_balance = df['Balance'].mean()
        previous_mean_balance = previous_df['mean_balance'].iloc[-1] if previous_df is not None else mean_balance

        with open('README.md', 'w') as readme_file:
            readme_file.write(f"# Zora Token Holders\n\n")
            readme_file.write(f"## Last updated: {current_time}\n\n")

            if previous_df is not None:
                readme_file.write(f"Holders with >1: {total_holders} ({total_holders - previous_df['total_holders'].iloc[-1]})\n")
                readme_file.write(f"Holders with >11: {holders_gt_11} ({holders_gt_11 - previous_df['holders_gt_11'].iloc[-1]})\n")
                readme_file.write(f"Holders with >111: {holders_gt_111} ({holders_gt_111 - previous_df['holders_gt_111'].iloc[-1]})\n")
                readme_file.write(f"Mean balance: {mean_balance} (previous {previous_mean_balance})\n")
            else:
                readme_file.write(f"Holders with >1: {total_holders}\n")
                readme_file.write(f"Holders with >11: {holders_gt_11}\n")
                readme_file.write(f"Holders with >111: {holders_gt_111}\n")
                readme_file.write(f"Mean balance: {mean_balance}\n")

        new_summary_row = pd.DataFrame({
            'total_holders': [total_holders],
            'holders_gt_11': [holders_gt_11],
            'holders_gt_111': [holders_gt_111],
            'mean_balance': [mean_balance]
        })

        new_summary_row.to_csv('previous_results.txt', mode='a', header=not os.path.exists('previous_results.txt'), index=False)

        print("README.md updated successfully.")
    except Exception as e:
        print(f"Failed to update README.md: {e}")
        traceback.print_exc()

    print("Data fetching and saving completed. Saved to data.csv, progression_data.csv, and README.md updated.")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
