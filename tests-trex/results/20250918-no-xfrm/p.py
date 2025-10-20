#!/opt/local/bin/python3.11

import json
import pandas as pd
import matplotlib.pyplot as plt

# List of JSON files
file_list = [
    "trex-flows-1-16-pps-1.37m-frame-size-9018.json",
    "trex-flows-1-16-pps-8.0m-frame-size-1518.json",
    "trex-flows-1-16-pps-128-frame-size-64.json",
    "trex-flows-1-16-pps-20m-frame-size-576.json",
    "trex-flows-1-16-pps-8.1m-frame-size-1518.json",
    "trex-flows-1-16-pps-129-frame-size-64.json",
    "trex-flows-1-16-pps-3m-frame-size-4096.json",
    "trex-flows-1-16-pps-9.5m-frame-size-1280.json",
    "trex-flows-1-16-pps-78m-frame-size-128.json.json"
]

# Read & flatten JSON data
all_records = []
for filename in file_list:
    with open(filename, 'r') as f:
        data = json.load(f)
        # Flatten nested lists into one list of dicts
        flat_list = [item for outer in data for inner in outer for item in inner]
        all_records.extend(flat_list)

# Create DataFrame
df = pd.DataFrame(all_records)

# Average by frame_size
avg_df = (
    df.groupby('frame_size')[['rx_pps', 'rx_throughput_gibps']]
    .mean()
    .reset_index()
    .sort_values('frame_size')
)

# Convert rx_pps to Mpps for readability
avg_df['rx_pps_mpps'] = avg_df['rx_pps'] / 1e6


# Create a reduced DataFrame with only needed columns
print_df = avg_df[['frame_size', 'rx_pps_mpps', 'rx_throughput_gibps']]

# Print with both values formatted to 2 decimal places
print(print_df.to_string(index=False, formatters={
    'rx_pps_mpps': '{:.2f}'.format,
    'rx_throughput_gibps': '{:.2f}'.format
}))

# Extract shared x-values
frame_sizes = avg_df['frame_size'].tolist()
y_pps_vals = avg_df['rx_pps_mpps']
y_gbps_vals = avg_df['rx_throughput_gibps']  # already ~72 for 128B

x_vals = avg_df['frame_size'].values  # shared X for both series
y_pps_vals = avg_df['rx_pps_mpps'].values
y_gbps_vals = avg_df['rx_throughput_gibps'].values

fig, ax1 = plt.subplots(figsize=(12, 6))

# Left axis
ax1.set_xlabel('Frame Size (bytes, log scale)')
ax1.set_ylabel('Average RX Throughput (Gbps)', color='tab:blue')
ax1.plot(x_vals, y_gbps_vals, marker='o', color='tab:blue', label='RX PPS (Mpps)', linewidth=3)
ax1.set_xscale('log')
ax1.set_xticks(x_vals)  # exact same X as data
ax1.set_xticklabels([str(x) for x in x_vals])
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.grid(True, which='both', axis='y')  # Only horizontal gridlines (y-axis)

for x in x_vals:
    ax1.axvline(x, color='gray', linestyle='-', linewidth=0.5, zorder=0)

# Right axis
ax2 = ax1.twinx()
ax2.set_ylabel('Average RX PPS (Mpps)', color='tab:red')
ax2.plot(x_vals, y_pps_vals, marker='s', linestyle='-', color='tab:red', label='RX Throughput (Gbps)', linewidth=3)
ax2.set_xticklabels([str(x) for x in x_vals])
ax2.tick_params(axis='y', labelcolor='tab:red')

# Extend y-axis limits to add padding
y1_min, y1_max = ax1.get_ylim()
y2_min, y2_max = ax2.get_ylim()
ax1.set_ylim(y1_min, y1_max * 1.01)  # Add 13% more space at the top
ax2.set_ylim(y2_min, y2_max * 1.13)  # Adjust factor as desired

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.title('Average Receive PPS and Throughput vs Frame Size')
plt.savefig("plot.png", dpi=300, bbox_inches='tight')

# df_9000 = df[df['frame_size'] == 9000]
# print(df_4096['rx_throughput_gibps'].mean())
# print(df_4096['rx_throughput_gibps'].min(), df_4096['rx_throughput_gibps'].max())
# print(df_4096.columns.tolist())
# for val in df_4096['rx_throughput_gibps']:
#    print(val)

# Save
# plt.savefig("plot.png", dpi=300, bbox_inches='tight')
# plt.show()
# print(df[df['frame_size'] == 128][['frame_size', 'rx_pps', 'rx_throughput_gibps']])
