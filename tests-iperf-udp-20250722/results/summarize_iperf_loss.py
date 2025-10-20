#!/usr/bin/python3
import os
import re
import csv
import argparse
from collections import defaultdict

# Argument parser setup
parser = argparse.ArgumentParser(
    description="Summarize iperf3 bandwidth (Gbps) per flow/run and compute average"
)

parser.add_argument(
        "--input-folder",
        type=str,
        default="20250721-iperf-udp-2G-flows-15",
        nargs="?",
        help="Optional output CSV filename. Defaults to <dirname>. Directory iperf3-<flows>-<run>-output\.txt"
)
parser.add_argument(
    "--output-csv",
    type=str,
    default = None,
    nargs="?",
    help="Optional output CSV filename. Defaults to <dirname>.csv"
)
args = parser.parse_args()

input_folder = args.input_folder
output_csv = args.output_csv or f"{os.path.basename(input_folder.rstrip('/'))}.csv"

# Validate directory
if not os.path.isdir(input_folder):
    print(f"Error: Directory '{input_folder}' not found.")
    exit(1)

filename_pattern = re.compile(r'iperf3-(\d+)-(\d+)-output\.txt')
data = defaultdict(dict)

# Read and parse files
for filename in os.listdir(input_folder):
    match = filename_pattern.match(filename)
    if not match:
        continue
    flows, run = match.groups()
    with open(os.path.join(input_folder, filename), 'r') as f:
        for line in f:
            if re.search(r'receiver\s*$', line):
                parts = line.strip().split()
                if len(parts) >= 8:
                    rate_str = parts[6]
                    unit = parts[7]
                    try:
                        rate = float(rate_str)
                        if unit == "Kbits/sec":
                            rate /= 1_000_000
                        elif unit == "Mbits/sec":
                            rate /= 1_000
                        elif unit == "Gbits/sec":
                            pass
                        else:
                            rate = 0.0
                        data[flows][run] = round(rate, 3)
                    except ValueError:
                        data[flows][run] = ""

# Sort and prepare header
all_runs = sorted({int(run) for runs in data.values() for run in runs})
header = ["Flows"] + [f"Run_{r}" for r in all_runs] + ["Avg_Gbps"]

# Print to console
print("#" + ",".join(header))
for flows in sorted(data.keys(), key=int):
    rates = [data[flows].get(str(r), "") for r in all_runs]
    rate_values = [v for v in rates if isinstance(v, float)]
    avg = round(sum(rate_values) / len(rate_values), 3) if rate_values else ""
    row = [flows] + [str(r) for r in rates] + [str(avg)]
    print(",".join(row))

# Write CSV
with open(output_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    for flows in sorted(data.keys(), key=int):
        rates = [data[flows].get(str(r), "") for r in all_runs]
        rate_values = [v for v in rates if isinstance(v, float)]
        avg = round(sum(rate_values) / len(rate_values), 3) if rate_values else ""
        writer.writerow([flows] + rates + [avg])

print(f"\nSummary written to: {output_csv}")
