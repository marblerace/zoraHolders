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
                if data is None:
                    print("Stopping further data fetching due to error.")
                    break
                if 'items' in data:
                    items = data.get('items', [])
                    holders_data.extend([[item['address']['hash'], item['value']] for item in items])
                    print(f"Fetched page with params: {next_page_params}")
                else:
                    print("No more data found or failed to fetch data.")
                    break
            else:
                print("No more pages to fetch.")
                break

    # Convert the list to a DataFrame and save only if data fetching completed successfully
    if data is not None:
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
        holders_gt_11 = df[df['Balance'] >= 11].shape[0]
        holders_gt_111 = df[df['Balance'] >= 111].shape[0]
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

        # Generate the results directly
        mean_balance = df['Balance'].mean()
        results = f"Holders with >1: {total_holders}\nHolders with >=11: {holders_gt_11}\nHolders with >=111: {holders_gt_111}\nMean balance: {mean_balance}\n"
        with open('results.txt', 'w') as f:
            f.write(results)

        # Plot the progression curves
        def plot_curve(progression_df, column, title, color, file_name):
            plt.figure(figsize=(10, 6))
            plt.plot(progression_df['timestamp'], progression_df[column], label=title, color=color)
            plt.xlabel('Time')
            plt.ylabel('Number of Holders')
            plt.title(f'Progression Curve - {title}')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.ylim(progression_df[column].min(), progression_df[column].max())
            yticks = progression_df[column].unique()
            plt.yticks(yticks)
            plt.tight_layout()
            plt.savefig(file_name)
            plt.close()

        try:
            plot_curve(progression_df, 'total_holders', 'All Holders', 'black', 'progression_curve_all.png')
            plot_curve(progression_df, 'holders_gt_11', 'Holders >=11', 'red', 'progression_curve_gt_11.png')
            plot_curve(progression_df, 'holders_gt_111', 'Holders >=111', 'blue', 'progression_curve_gt_111.png')

            print("Progression curve graphs saved successfully.")
        except Exception as e:
            print(f"Failed to plot and save progression curve graphs: {e}")
            traceback.print_exc()

        print("Data fetching and saving completed. Saved to data.csv, progression_data.csv, and results.txt updated.")
    else:
        print("Data fetching halted due to server error; data.csv not updated.")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
