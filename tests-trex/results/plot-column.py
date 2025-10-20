#!/usr/bin/env python3
"""
A modular rewrite of the original pps-plot.py that plots FOUR lines
on a single chart: the original file + three additional variants.

Defaults (edit the list or pass --files):
- trex-flows-1-15-frame-size-128-16m.json.json
- trex-flows-1-15-frame-size-128-16m-no-bulk.json.json
- trex-flows-1-15-frame-size-128-16m-west-bulk.json.json
- trex-flows-1-15-frame-size-128-16m-east-bulk.json.json
"""

import argparse
import json
from pathlib import Path
from typing import List, Tuple, Optional
from matplotlib.ticker import FixedLocator, FuncFormatter


import pandas as pd
import matplotlib.pyplot as plt

def pow2_ticks(xmin: float, xmax: float):
    """Return powers of two within [xmin, xmax]."""
    vals = []
    v = 1
    while v < xmin:
        v *= 2
    while v <= xmax:
        vals.append(v)
        v *= 2
    return vals

def pow2_formatter(v, pos):
    """Format powers of two, using K when v % 1024 == 0."""
    if v % 1024 == 0:
        return f"{int(v/1024)}K"
    else:
        return f"{int(v)}"

def load_json_flat(path: Path) -> pd.DataFrame:
    """Load and flatten a JSON file into a DataFrame.

    Supports arrays of objects and object dictionaries. We try to normalize
    nested structures so columns like 'flows' and 'avg_recv_pps' become top-level.
    """
    with open(path, "r") as f:
        data = json.load(f)

    # If it's already a list of dicts:
    if isinstance(data, list):
        return pd.json_normalize(data)

    # If dict, try common containers:
    if isinstance(data, dict):
        for key in ("data", "results", "items", "rows", "payload"):
            if key in data and isinstance(data[key], list):
                return pd.json_normalize(data[key])
        # Fallback: normalize dict (single row case)
        return pd.json_normalize(data)

    # Fallback empty
    return pd.DataFrame()


def find_columns(df: pd.DataFrame, x_candidates: List[str], y_candidates: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """Return the first matching x and y column names based on candidates (case-insensitive)."""
    lower_map = {c.lower(): c for c in df.columns}
    x_col = next((lower_map[c] for c in x_candidates if c in lower_map), None)
    y_col = next((lower_map[c] for c in y_candidates if c in lower_map), None)
    return x_col, y_col


def prep_xy(df: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    """Return a two-column, x-sorted dataframe with numeric coercion where possible."""
    out = df[[x_col, y_col]].copy()
    out[x_col] = pd.to_numeric(out[x_col], errors="ignore")
    out[y_col] = pd.to_numeric(out[y_col], errors="ignore")
    try:
        out = out.sort_values(by=x_col)
    except Exception:
        pass
    return out



def label_from_filename(path: Path) -> str:
    """Readable label from filename — remove all trailing .json, replace '-' with space,
    and capitalize the first letter."""
    name = path.name
    # Remove all trailing .json extensions
    while name.endswith(".json"):
        name = name[:-5]

    # Replace dashes with spaces to increast readability
    name = name.replace("-", " ")

    # Capitalize the first character
    if name:
        name = name[0].upper() + name[1:]

    return name


def plot_multiple(files, x_key: Optional[str], y_key: Optional[str], title: str, out_path: Path, x_label, y_label, x_log_2) -> None:
    """Plot all provided files as separate lines on one chart and save the figure."""
    if not files:
        raise SystemExit("No input files given.")

    # Candidate columns (case-insensitive matching)
    x_candidates = ["flows", "dst_ports"]
    y_candidates = ['rx_pps', "rx_throughput_gibps" ]

    fig, ax = plt.subplots(figsize=(10, 6))

    used_x = x_key
    used_y = y_key

    for fpath in files:
        df = load_json_flat(Path(fpath))
        if df.empty:
            print(f"[WARN] {fpath} produced empty data; skipping.")
            continue

        cur_x = used_x
        cur_y = used_y

        if cur_x is None or cur_y is None:
            auto_x, auto_y = find_columns(df, x_candidates, y_candidates)
            if cur_x is None:
                cur_x = auto_x
            if cur_y is None:
                cur_y = auto_y

        if cur_x is None or cur_y is None:
            print(f"[WARN] Could not detect x/y columns for {fpath}. Columns: {list(df.columns)}; skipping.")
            continue

        # Average by X (e.g., flows) and sort
        grp = (
            df.groupby(cur_x)[[cur_y]]
            .mean(numeric_only=True)
            .reset_index()
            .sort_values(cur_x)
        )

        # Convert PPS to Mpps if the Y column looks like PPS
        y_series = grp[cur_y]
        if "pps" in cur_y.lower():
            y_plot = y_series / 1e6
        else:
            y_plot = y_series

        # First file decides axis labels
        if used_x is None:
            used_x = cur_x
        if used_y is None:
            used_y = y_label  # show units if we converted

        # Plot this file as its own line (no merging between files)
        ax.plot(grp[cur_x], y_plot, marker="o", linewidth=2, label=label_from_filename(Path(fpath)))

        # Track global x-range for vertical guidelines
        try:
            x_vals = pd.to_numeric(grp[cur_x], errors="coerce")
            mn = x_vals.min(skipna=True)
            mx = x_vals.max(skipna=True)
            if pd.notna(mn):
                global_x_min = mn if global_x_min is None else min(global_x_min, mn)
            if pd.notna(mx):
                global_x_max = mx if global_x_max is None else max(global_x_max, mx)
        except Exception:
            pass

    # Labels and grid
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(True, which="both", axis="both", linestyle="--", linewidth=0.5)

    # Add thin vertical guidelines at integer x if x is reasonably small
    try:
        x_min, x_max = ax.get_xlim()
        x_span = int(round(x_max - x_min))
        if x_span <= 500:
            start = int(round(x_min))
            end = int(round(x_max))
            for xv in range(start, end + 1):
                ax.axvline(x=xv, linestyle="-", linewidth=0.3, alpha=0.4, zorder=0)
    except Exception:
        pass

    # Extend y-axis a bit for headroom
    y1_min, y1_max = ax.get_ylim()
    ax.set_ylim(y1_min, y1_max * 1.1)

    if x_log_2:
        ax.set_xscale("log", base=2)
        # ax.set_xticklabels([str(v) for v in x_vals], rotation=30, ha='right')
        xmin, xmax = ax.get_xlim()
        ticks = pow2_ticks(xmin, xmax)
        if ticks:
          ax.xaxis.set_major_locator(FixedLocator(ticks))
          ax.xaxis.set_major_formatter(FuncFormatter(pow2_formatter))

       # Optional: rotate labels
        for label in ax.get_xticklabels():
          label.set_rotation(30)
          label.set_ha("right")

        print(f"{x_vals}")
        print(f"{ticks}")

    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"[OK] Saved figure to {out_path}")


def parse_args():
    p = argparse.ArgumentParser(description="Plot 4 TRex results on one chart.")
    p.add_argument(
        "--files", nargs="+", default=[
            "trex-flows-1-15-frame-size-128-16m.json.json",
            "trex-flows-1-15-frame-size-128-16m-no-bulk.json.json",
            "trex-flows-1-15-frame-size-128-16m-west-bulk.json.json",
            "trex-flows-1-15-frame-size-128-16m-east-bulk.json.json",
        ],
        help="Input JSON files. Default includes base + no-bulk + west-bulk + east-bulk."
    )
    p.add_argument( "--x-log-2", action="store_true", help="Use log₂ scale for the X axis (default: linear)."
)
    p.add_argument("--x-key", default="flows", help="X column (default: 'flows').")
    p.add_argument("--y-key", default="rx_pps", help="Y column (default: 'rx_pps').")
    p.add_argument("--x-label", default=None, help="Custom label for X-axis. Defaults to --x-key.")
    p.add_argument("--y-label", default=None, help="Custom label for Y-axis. Defaults to --y-key.")
    p.add_argument("--title", default="Average Receive PPS vs Flows (4 variants)", help="Plot title.")
    p.add_argument("--out", default="pps-plot.png", help="Output PNG path.")
    return p.parse_args()


def main():
    args = parse_args()

    # Default labels to keys if not provided
    x_label = args.x_label or args.x_key
    y_label = args.y_label or args.y_key

    plot_multiple(
        files=args.files,
        x_key=args.x_key,
        y_key=args.y_key,
        title=args.title,
        out_path=Path(args.out),
        x_label=x_label,
        y_label=y_label,
        x_log_2=args.x_log_2,
    )


if __name__ == "__main__":
    main()
