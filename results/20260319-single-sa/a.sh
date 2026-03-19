#!/bin/bash
: ${SUBDIR=../results/20260318-single-sa}
mkdir -p $SUBDIR
# ./u1.py --pps 0.27M --pps 0.28M  --pps 0.3M --pps 0.31M --pps 0.32M  --frame-size 1460 --duration 10 --results-file $SUBDIR/trex-1500.json
./u1.py --pps 0.17M --pps 0.18M  --pps 0.2M --pps 0.21M --pps 0.22M  --frame-size 8960 --duration 10 --results-file $SUBDIR/trex-9000.json
