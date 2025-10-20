#!/bin/python3

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
    baseline = pd.read_csv(f'./trex_results-12-2g{mtu_file_suffix}-no-ipsec.csv', skiprows=1)
    tunnel = pd.read_csv(f'./trex_results-12-2g{mtu_file_suffix}-one-sa.csv', skiprows=1)
    pcpu = pd.read_csv(f'./trex_results-12-2g{mtu_file_suffix}-pcpu.csv', skiprows=1)

    # Extract the values for plotting
    baseline_x = baseline['#flows']
    baseline_y = baseline['avg_5']
    tunnel_x = tunnel['#flows']
    tunnel_y = tunnel['avg_5']
    pcpu_x = pcpu['#flows']
    pcpu_y = pcpu['avg_5']

    # Create the plot
    plt.figure(figsize=(12, 6))
    # plt.axvline(x=16, color='r', linestyle='-', label='Number of CPUs')


    import matplotlib.pyplot as plt

    # Your plotting code
    plt.plot(baseline_x, baseline_y, '--', label=f'Plaintext UDP 2 Gbps (max {baseline_y.max():.2f})')
    plt.plot(tunnel_x, tunnel_y, '--', label=f'Single tunnel UDP 2 Gbps (max {tunnel_y.max():.2f})')
    plt.plot(pcpu_x, pcpu_y, '-o', label=f'Percpu tunnel UDP 2 Gbps (max {pcpu_y.max():.2f})')

    plt.title(f'Average Throughput vs. Number of Flows {mtu_str}')

    legend = plt.legend(loc='upper left')

    # Get legend bounding box in display coordinates
    bbox = legend.get_window_extent()

    # Transform bounding box to axes coordinates
    inv = plt.gca().transAxes.inverted()
    bbox_axes = bbox.transformed(inv)

    # Coordinates just below the legend box (x same as legend left edge)
    x = bbox_axes.x0
    y = bbox_axes.y0 - 0.05  # move 0.05 down; adjust as needed for spacing

    # Add text box below legend
    plt.text(
        x, y,
        "TRex Unidirectional UDP Flows",
        fontsize=8,
        ha='left', va='top',
        transform=plt.gca().transAxes,
        bbox=dict(facecolor='white', alpha=0.3, boxstyle='round,pad=0.3')
    )


    plt.xlabel('#Flows')
    plt.ylabel('Average (Gbps)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(f"plot{mtu_file_suffix}.png", dpi=300, bbox_inches='tight')
