#!/opt/local/bin/python3.11

import json
import pandas as pd
import matplotlib.pyplot as plt

# List of JSON files
file_list = [
    "trex-flows-1-15-frame-size-128-16m.json.json"
]

# Read & flatten JSON data
for filename in file_list:
    with open(filename, 'r') as f:
        flat_list = json.load(f)

# Create DataFrame
df = pd.DataFrame(flat_list)

# Average by run
avg_df = (
    df.groupby('flows')[['rx_pps']]
    .mean()
    .reset_index()
    .sort_values('flows')
)

# Convert rx_pps to Mpps for readability
avg_df['rx_pps_mpps'] = avg_df['rx_pps'] / 1e6

# Create a reduced DataFrame with only needed columns
print_df = avg_df[['flows', 'rx_pps_mpps']]

# Print with both values formatted to 2 decimal places
print(print_df.to_string(index=False, formatters={
    'flows': '{:}'.format,
    'rx_pps_mpps': '{:.2f}'.format,
}))

# Extract shared x-values
flows = avg_df['flows'].tolist()
y_pps_vals = avg_df['rx_pps_mpps']

x_vals = avg_df['flows'].values  # shared X for both series
y_pps_vals = avg_df['rx_pps_mpps'].values

fig, ax = plt.subplots(figsize=(12, 6))

# Left axis
ax.set_xlabel('Flows')
ax.set_ylabel('Average RX PPS (MPPS)', color='tab:blue')
ax.plot(x_vals, y_pps_vals, marker='o', color='tab:blue', label='Bulk RX Gbps', linewidth=3)
ax.set_xticks(x_vals)  # exact same X as data
ax.set_xticklabels([str(x) for x in x_vals])
ax.tick_params(axis='y', labelcolor='tab:blue')
ax.grid(True, which='both', axis='y')  # Only horizontal gridlines (y-axis)

for x in x_vals:
    ax.axvline(x, color='gray', linestyle='-', linewidth=0.5, zorder=0)

# Extend y-axis limits to add padding
y1_min, y1_max = ax.get_ylim()
ax.set_ylim(y1_min, y1_max * 1.1)  # Add more space at the top

# Legend
lines1, labels1 = ax.get_legend_handles_labels()
ax.legend(lines1, labels1, loc='upper left')

plt.title('Average Receive PPS vs Flows: frame size 128 bytes')
plt.savefig("pps-plot.png", dpi=300, bbox_inches='tight')
