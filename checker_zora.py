import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
csv_file = 'data.csv'
df = pd.read_csv(csv_file)

# Total number of holders
total_holders = df.shape[0]

# Number of holders with specific quantity conditions
holders_5 = df[df['Quantity'] > 5].shape[0]
holders_10 = df[df['Quantity'] > 10].shape[0]
holders_11 = df[df['Quantity'] > 11].shape[0]
holders_25 = df[df['Quantity'] > 25].shape[0]
holders_50 = df[df['Quantity'] > 50].shape[0]
holders_100 = df[df['Quantity'] > 100].shape[0]
holders_111 = df[df['Quantity'] > 111].shape[0]

# Statistics
min_quantity = df['Quantity'].min()
max_quantity = df['Quantity'].max()
median_quantity = df['Quantity'].median()
mean_quantity = df['Quantity'].mean()

# Save the results to a file
with open('results.txt', 'w') as file:
    file.write(f"Total holders: {total_holders}\n")
    file.write(f"Holders with >5: {holders_5}\n")
    file.write(f"Holders with >10: {holders_10}\n")
    file.write(f"Holders with >11: {holders_11}\n")
    file.write(f"Holders with >25: {holders_25}\n")
    file.write(f"Holders with >50: {holders_50}\n")
    file.write(f"Holders with >100: {holders_100}\n")
    file.write(f"Holders with >111: {holders_111}\n")
    file.write(f"Min quantity: {min_quantity}\n")
    file.write(f"Max quantity: {max_quantity}\n")
    file.write(f"Median quantity: {median_quantity}\n")
    file.write(f"Mean quantity: {mean_quantity}\n")

# Create a column type graph with 1 step increments
quantities = list(range(1, int(max_quantity) + 1))
holder_counts = [df[df['Quantity'] == q].shape[0] for q in quantities]

plt.figure(figsize=(15, 8))
plt.bar(quantities, holder_counts, color='skyblue')
plt.xlabel('Quantity')
plt.ylabel('Number of Holders')
plt.title('Number of Holders by Quantity')
plt.xticks(range(0, int(max_quantity) + 1, max(1, int(max_quantity) // 20)))  # Adjusting x-axis ticks for readability
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('holders_by_quantity.png')
plt.close()
