#!/opt/local/bin/python3.11

import json
import pandas as pd
import matplotlib.pyplot as plt

# List of JSON files
file_list = [
    "bulk-xfrm/trex-flows-256-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-1-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-4-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-1014-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-4096-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-128-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-512-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-16-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-8-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-16384-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-8192-frame-size-128-bulk-xfrm.json",
    "bulk-xfrm/trex-flows-2-frame-size-128-bulk-xfrm.json"
]

# Read JSON data
all_records = []
for filename in file_list:
    with open(filename, 'r') as f:
        flat_list = json.load(f)
        all_records.extend(flat_list)

# Create DataFrame
df = pd.DataFrame(all_records)

# Average by run
avg_df = (
    df.groupby('dst_ports')[['rx_pps', 'rx_throughput_gibps']]
    .mean()
    .reset_index()
    .sort_values('dst_ports')
)

# Convert rx_pps to Mpps for readability
avg_df['rx_pps_mpps'] = avg_df['rx_pps'] / 1e6

# Create a reduced DataFrame with only needed columns
print_df = avg_df[['dst_ports', 'rx_pps_mpps', 'rx_throughput_gibps']]

# Print with both values formatted to 2 decimal places
print(print_df.to_string(index=False, formatters={
    'dst_ports': '{:}'.format,
    'rx_pps_mpps': '{:.2f}'.format,
    'rx_throughput_gibps': '{:.2f}'.format
}))

# Extract shared x-values
dst_ports = avg_df['dst_ports'].tolist()
y_pps_vals = avg_df['rx_pps_mpps']
y_gbps_vals = avg_df['rx_throughput_gibps']  # already ~72 for 128B

x_vals = avg_df['dst_ports'].values  # shared X for both series
y_pps_vals = avg_df['rx_pps_mpps'].values
y_gbps_vals = avg_df['rx_throughput_gibps'].values

fig, ax1 = plt.subplots(figsize=(12, 6))

# Left axis
ax1.set_xlabel('Flows scale')
ax1.set_ylabel('Average RX Throughput (Gbps)', color='tab:blue')
ax1.plot(x_vals, y_gbps_vals, marker='o', color='tab:blue', label='RX Gbps', linewidth=3)
ax1.set_xticks(x_vals) # set exact positions for ticks
ax1.set_xticklabels([str(v) for v in x_vals], rotation=30, ha='right')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.grid(True, which='both', axis='y')  # Only horizontal gridlines (y-axis)
ax1.set_xscale('log', base=2)

for x in x_vals:
    ax1.axvline(x, color='gray', linestyle='-', linewidth=0.5, zorder=0)

# Right axis
ax2 = ax1.twinx()
ax2.set_ylabel('Average RX PPS (Mpps)', color='tab:red')
ax2.plot(x_vals, y_pps_vals, marker='s', linestyle='-', color='tab:red', label='RX PPS (Mpps)', linewidth=3)
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

plt.title('Average Receive PPS and Throughput vs Flows: frame size 128 bytes')
plt.tight_layout()
plt.savefig("plot.png", dpi=300, bbox_inches='tight')
