#!/opt/local/bin/python3.11

import pandas as pd
import matplotlib.pyplot as plt

for mtu in [1440]:
    if mtu:
        mtu_file_suffix = f"-{mtu}"
        mtu_str = f" ({mtu} MTU)"
    else:
        mtu_file_suffix = ""
        mtu_str = f" (1380 MTU)"

    # Load the data into DataFrames
    baseline = pd.read_csv(f'./trex_results-1-16-3.3G{mtu_file_suffix}-no-ipsec.csv', skiprows=1)
    tunnel = pd.read_csv(f'./trex_results-1-16-3.3G{mtu_file_suffix}-one-sa.csv', skiprows=1)
    pcpu = pd.read_csv(f'./trex_results-1-16-3.3G{mtu_file_suffix}-pcpu.csv', skiprows=1)
    pcpu_err = pd.read_csv(f'./trex_results-1-16-3.3G{mtu_file_suffix}-pcpu-lp.csv')

    # Extract the values for plotting
    baseline_x = baseline['#flows']
    baseline_y = baseline['avg_5']
    tunnel_x = tunnel['#flows']
    tunnel_y = tunnel['avg_5']
    pcpu_x = pcpu['#flows']
    pcpu_y = pcpu['avg_5']

    # Create the main plot and plot baseline, tunnel, pcpu on primary y-axis
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(baseline_x, baseline_y, '--', label=f'Plaintext UDP 3.3 Gbps (max {baseline_y.max():.2f})')
    ax.plot(tunnel_x, tunnel_y, '--', label=f'Single tunnel UDP 3.3 Gbps (max {tunnel_y.max():.2f})')
    ax.plot(pcpu_x, pcpu_y, '-o', label=f'pCPU tunnel UDP 3.3 Gbps (max {pcpu_y.max():.2f})')

    # Create a secondary y-axis for pcpu_err (dropped packets %)
    ax2 = ax.twinx()

    pcpu_err_x = pcpu_err['#flows']
    pcpu_err_y = pcpu_err['cum_error']  # dropped packet percentage column

    ax2.plot(pcpu_err_x, pcpu_err_y, '-s', color='tab:red', label=f'pCPU Error % (max {pcpu_err_y.max():.2f})')

    # Labeling axes
    ax.set_xlabel('#Flows')
    ax.set_ylabel('Average Throughput (Gbps)')
    ax2.set_ylabel('Percentage Dropped Packets (%)')

    # Grids (only on primary axis to avoid clutter, optional you can enable for ax2 as well)
    ax.grid(True)
    # ax2.grid(True)  # Enable if you want grid lines for secondary axis

    plt.title(f'Average Throughput vs. Number of Flows{mtu_str}')

    # Combine legends from both axes into one
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Calculate legend box and position text below it
    legend = ax.get_legend()
    bbox = legend.get_window_extent()
    inv = plt.gca().transAxes.inverted()
    bbox_axes = bbox.transformed(inv)

    x = bbox_axes.x0
    y = bbox_axes.y0 - 0.04  # adjust downward as needed

    plt.text( x, y,
        "3.3 Gbps TRex Unidirectional UDP Flows",
        fontsize=8, ha='left', va='top',
        transform=plt.gca().transAxes,
        bbox=dict(facecolor='white', alpha=0.3, boxstyle='round,pad=0.3')
    )

    plt.tight_layout()

    # Save the plot to a PNG file
    plt.savefig(f"plot{mtu_file_suffix}.png", dpi=300, bbox_inches='tight')

    # plt.show()
