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
        results = f"Holders with > 1: {total_holders}\nHolders with >= 11: {holders_gt_11}\nHolders with >= 111: {holders_gt_111}\nMean balance: {mean_balance}\n"
        with open('results.txt', 'w') as f:
            f.write(results)

        # Prepare timestamps for plotting
        progression_df['timestamp_dt'] = pd.to_datetime(progression_df['timestamp'], format='%d-%m-%Y %H:%M')

        # Plot the progression curves
        def plot_curve(progression_df, column, title, color, file_name, ytick_values=None):
            plt.figure(figsize=(10, 6))

            # Plot the progression data using real datetimes for the x-axis
            times = progression_df['timestamp_dt']
            values = progression_df[column]
            plt.plot(times, values, label=title, color=color)

            # Build x-ticks: first check of each month, labeled with the month name
            df_for_ticks = progression_df.dropna(subset=['timestamp_dt']).sort_values('timestamp_dt')
            month_starts = df_for_ticks.groupby(df_for_ticks['timestamp_dt'].dt.to_period('M'))['timestamp_dt'].first()
            month_positions = pd.to_datetime(month_starts.values)
            month_labels = month_starts.dt.strftime('%b')
            plt.xticks(month_positions, month_labels, rotation=45)

            # Remove horizontal and vertical bars (main grid)
            plt.grid(False)

            max_val = values.max()
            min_val = values.min()

            # Generate y-ticks: either custom values or every integer in range
            if ytick_values is None:
                yticks = list(range(int(min_val), int(max_val) + 1))
            else:
                yticks = ytick_values

            y_min = min(min_val, min(yticks))
            y_max = max(max_val, max(yticks))

            plt.yticks(yticks)

            # Add horizontal grid lines only for the y-ticks
            plt.gca().yaxis.grid(True, which='major', linestyle='--', color='gray')

            # Set labels and title
            plt.xlabel('Date')
            plt.ylabel('Number of Holders')
            plt.title(f'Progression Curve - {title}')

            # Apply the y-axis limits after ticks are defined
            plt.ylim(y_min, y_max)

            # Save the figure
            plt.tight_layout()
            plt.savefig(file_name)
            plt.close()

        try:
            # Sample usage of the function with different y-tick intervals
            plot_curve(progression_df, 'total_holders', 'addresses with >= 1 mints', 'black', 'progression_curve_all.png', [1800, 1900, 2000, 2100])
            plot_curve(progression_df, 'holders_gt_11', 'addresses with >= 11 mints', 'red', 'progression_curve_gt_11.png', [120, 130, 140, 150, 160])
            plot_curve(progression_df, 'holders_gt_111', 'addresses with >= 111 mints', 'blue', 'progression_curve_gt_111.png', None)

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
