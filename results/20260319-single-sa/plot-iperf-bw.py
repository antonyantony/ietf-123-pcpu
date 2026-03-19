#!/usr/bin/env python3
"""Plot iperf3 send/receive bandwidth with error bars (best and average) for TCP and UDP.

Discovers all iperf-mtu-* subdirectories automatically and produces one PNG per MTU.
Run from the directory containing the iperf-mtu-* folders.
"""

import json
import glob
import os
import re
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data(mtu_dir):
    """Load all JSON files from mtu_dir, organised by protocol and target bandwidth."""
    data = defaultdict(lambda: defaultdict(list))
    for path in glob.glob(os.path.join(mtu_dir, "*.json")):
        m = re.match(r".*/([a-z]+)-(\d+)-(\d+)G-\d+\.json", path)
        if not m:
            continue
        proto, gbps = m.group(1), int(m.group(3))
        with open(path) as f:
            d = json.load(f)
        sent = d["end"]["sum_sent"]["bits_per_second"] / 1e9
        recv = d["end"]["sum_received"]["bits_per_second"] / 1e9
        data[proto][gbps].append((sent, recv))
    return data


def plot_panel(data, mode, ax, mtu):
    targets = sorted({gbps for proto in data for gbps in data[proto]})
    x = np.arange(len(targets))
    bar_w = 0.18
    offsets = {"tcp_sent": -1.5, "tcp_recv": -0.5, "udp_sent": 0.5, "udp_recv": 1.5}
    colors  = {"tcp_sent": "#1f77b4", "tcp_recv": "#aec7e8",
                "udp_sent": "#d62728", "udp_recv": "#f5a9a9"}
    labels  = {"tcp_sent": "TCP sent", "tcp_recv": "TCP recv",
                "udp_sent": "UDP sent", "udp_recv": "UDP recv"}

    for proto in ("tcp", "udp"):
        for direction in ("sent", "recv"):
            key = f"{proto}_{direction}"
            vals, errs = [], []
            for gbps in targets:
                runs = data[proto].get(gbps, [])
                if not runs:
                    vals.append(0); errs.append(0)
                    continue
                sents = [r[0] for r in runs]
                recvs = [r[1] for r in runs]
                arr = sents if direction == "sent" else recvs
                if mode == "best":
                    best_idx = int(np.argmax(sents))
                    vals.append(arr[best_idx])
                else:
                    vals.append(np.mean(arr))

            ax.bar(
                x + offsets[key] * bar_w,
                vals,
                bar_w,
                label=labels[key],
                color=colors[key],
                edgecolor="black",
                linewidth=0.5,
            )

    ax.set_xticks(x)
    ax.set_xticklabels([f"{g}G" for g in targets])
    ax.set_xlabel("Target send bandwidth")
    ax.set_ylabel("Throughput (Gbps)")
    ax.set_title(f"MTU {mtu} — {mode.capitalize()} of 5 runs")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(axis="y", linestyle="--", alpha=0.5)


def main():
    mtu_dirs = sorted(glob.glob(os.path.join(SCRIPT_DIR, "iperf-mtu-*")))
    if not mtu_dirs:
        print("No iperf-mtu-* directories found.")
        return

    for mtu_dir in mtu_dirs:
        mtu = re.search(r"iperf-mtu-(\d+)", mtu_dir).group(1)
        data = load_data(mtu_dir)
        if not data:
            print(f"No data in {mtu_dir}, skipping.")
            continue

        fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
        fig.suptitle(f"iperf3 Bandwidth (MTU {mtu}): TCP vs UDP, Sent vs Received", fontsize=13)

        plot_panel(data, "best",    axes[0], mtu)
        plot_panel(data, "average", axes[1], mtu)

        plt.tight_layout()
        out = os.path.join(SCRIPT_DIR, f"iperf-bw-mtu{mtu}.png")
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
