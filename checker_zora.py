import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
csv_file = 'data.csv'
df = pd.read_csv(csv_file)

# Total number of holders
total_holders = df.shape[0]

# Convert Balance to numeric, handling any non-numeric entries
df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')

# Number of holders with specific balance conditions
holders_5 = df[df['Balance'] > 5].shape[0]
holders_10 = df[df['Balance'] > 10].shape[0]
holders_11 = df[df['Balance'] > 11].shape[0]
holders_25 = df[df['Balance'] > 25].shape[0]
holders_50 = df[df['Balance'] > 50].shape[0]
holders_100 = df[df['Balance'] > 100].shape[0]
holders_111 = df[df['Balance'] > 111].shape[0]

# Statistics
min_balance = df['Balance'].min()
max_balance = df['Balance'].max()
median_balance = df['Balance'].median()
mean_balance = df['Balance'].mean()

# Read the previous results from previous_results.txt
try:
    with open('previous_results.txt', 'r') as file:
        lines = file.readlines()
        prev_total_holders = int(lines[0].split(': ')[1])
        prev_holders_5 = int(lines[1].split(': ')[1])
        prev_holders_10 = int(lines[2].split(': ')[1])
        prev_holders_11 = int(lines[3].split(': ')[1])
        prev_holders_25 = int(lines[4].split(': ')[1])
        prev_holders_50 = int(lines[5].split(': ')[1])
        prev_holders_100 = int(lines[6].split(': ')[1])
        prev_holders_111 = int(lines[7].split(': ')[1])
        prev_min_balance = float(lines[8].split(': ')[1])
        prev_max_balance = float(lines[9].split(': ')[1])
        prev_median_balance = float(lines[10].split(': ')[1])
        prev_mean_balance = float(lines[11].split(': ')[1])
except FileNotFoundError:
    prev_total_holders = prev_holders_5 = prev_holders_10 = prev_holders_11 = prev_holders_25 = prev_holders_50 = prev_holders_100 = prev_holders_111 = 0
    prev_min_balance = prev_max_balance = 0
    prev_median_balance = prev_mean_balance = 0.0

# Save the current results to results.txt
with open('results.txt', 'w') as file:
    file.write(f"Total holders: {total_holders} ({total_holders - prev_total_holders:+d})\n")
    file.write(f"Holders with >5: {holders_5} ({holders_5 - prev_holders_5:+d})\n")
    file.write(f"Holders with >10: {holders_10} ({holders_10 - prev_holders_10:+d})\n")
    file.write(f"Holders with >11: {holders_11} ({holders_11 - prev_holders_11:+d})\n")
    file.write(f"Holders with >25: {holders_25} ({holders_25 - prev_holders_25:+d})\n")
    file.write(f"Holders with >50: {holders_50} ({holders_50 - prev_holders_50:+d})\n")
    file.write(f"Holders with >100: {holders_100} ({holders_100 - prev_holders_100:+d})\n")
    file.write(f"Holders with >111: {holders_111} ({holders_111 - prev_holders_111:+d})\n")
    file.write(f"Min balance: {min_balance} (previous {prev_min_balance})\n")
    file.write(f"Max balance: {max_balance} (previous {prev_max_balance})\n")
    file.write(f"Median balance: {median_balance} (previous {prev_median_balance})\n")
    file.write(f"Mean balance: {mean_balance} (previous {prev_mean_balance})\n")

# Save the current results to previous_results.txt
with open('previous_results.txt', 'w') as file:
    file.write(f"Total holders: {total_holders}\n")
    file.write(f"Holders with >5: {holders_5}\n")
    file.write(f"Holders with >10: {holders_10}\n")
    file.write(f"Holders with >11: {holders_11}\n")
    file.write(f"Holders with >25: {holders_25}\n")
    file.write(f"Holders with >50: {holders_50}\n")
    file.write(f"Holders with >100: {holders_100}\n")
    file.write(f"Holders with >111: {holders_111}\n")
    file.write(f"Min balance: {min_balance}\n")
    file.write(f"Max balance: {max_balance}\n")
    file.write(f"Median balance: {median_balance}\n")
    file.write(f"Mean balance: {mean_balance}\n")

# Create a column type graph with 1 step increments
balances = list(range(1, int(max_balance) + 1))
holder_counts = [df[df['Balance'] == q].shape[0] for q in balances]

plt.figure(figsize=(15, 8))
plt.bar(balances, holder_counts, color='skyblue')
plt.xlabel('Balance')
plt.ylabel('Number of Holders')
plt.title('Number of Holders by Balance')
plt.xticks(range(0, int(max_balance) + 1, max(1, int(max_balance) // 20)))  # Adjusting x-axis ticks for readability
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('holders_by_balance.png')
plt.close()
