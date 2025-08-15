#!/bin/python3

import json
import csv
import argparse
from collections import defaultdict


def flatten_entries(entries):
    flat = []
    for e in entries:
        if isinstance(e, list):
            flat.extend(flatten_entries(e))
        else:
            flat.append(e)
    return flat


def main():
    parser = argparse.ArgumentParser(description="Generate CSV of lost packet percentages per flow and run")
    parser.add_argument("--input-json-file", default="trex_results-1-16-3.3G-1440-pcpu.json",
                        help="Input JSON file with test results")
    parser.add_argument("--output-lost-percentage", default="trex_results-1-16-3.3G-1440-pcpu-lp.csv",
                        help="Output CSV file to write lost packet percentages")
    args = parser.parse_args()

    # Load JSON file
    with open(args.input_json_file, 'r') as f:
        data = json.load(f)

    entries = flatten_entries(data)

    # Data structure:
    # We'll organize as: flows[flow_number][run_number] = l_pkts_percent
    flows = defaultdict(dict)

    # Collect runs for each flow number
    # Determine max run count (assuming runs are 1 indexed)
    runs_count = 0
    for entry in entries:
        flow = entry.get("flow")
        run = entry.get("run")
        l_pkts_percent = entry.get("l_pkts_percent", 0.0)
        flows[flow][run] = l_pkts_percent
        if run > runs_count:
            runs_count = run

    # Prepare CSV header
    # run_1, run_2 ... run_n
    header = ["#flows"]
    for run_i in range(1, runs_count + 1):
        header.append(f"run_{run_i}")
    header.append("cum_error")

    # Write CSV
    with open(args.output_lost_percentage, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        # Iterate flow numbers sorted ascending
        for flow_num in sorted(flows.keys()):
            row = [flow_num]
            # Collect per-run values, fill zero if missing
            run_values = []
            for run_i in range(1, runs_count + 1):
                val = flows[flow_num].get(run_i, 0.0)
                run_values.append(val)
                # Format to 2 decimal points
                row.append(f"{val:.2f}")

            # cumulative error as average of all runs for that flow
            cum_error = sum(run_values) / len(run_values) if run_values else 0.0
            row.append(f"{cum_error:.2f}")

            writer.writerow(row)

    print(f"Wrote lost packet percentage CSV to: {args.output_lost_percentage}")

if __name__ == "__main__":
    main()
