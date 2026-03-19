#!/bin/bash
../../tests-trex/results/plot-column.py --plot-bars \
    --files trex-1500.json \
    --title "TRex UDP throughput MTU 1500" \
    --out trex-bars-1500.png

../../tests-trex/results/plot-column.py --plot-bars \
    --files trex-9000.json \
    --title "TRex UDP throughput MTU 9000" \
    --out trex-bars-9000.png
