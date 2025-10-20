#!/bin/bash

set -eu

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number-of-threads>"
    exit 1
fi
NPATH=/root/neper/
NUM_THREADS=$1
RUNS="${RUNS:-5}"
CSV="${CSV:-}"

THROUGHPUTS=()
SUM=0

# Collecting throughput data and calculating the sum
for i in $(seq 1 ${RUNS}); do
    THROUGHPUT=$($NPATH/udp_stream --num-threads $NUM_THREADS --pin-cpu --nolog | awk -F '=' '/^throughput=/ { print $2 }')

    THROUGHPUTS+=($THROUGHPUT)
    SUM=$(echo "$SUM + $THROUGHPUT" | bc)

    if [ -z "$CSV" ]; then
      echo "Throughput (Run $i): $THROUGHPUT"
    fi
done


# Print CSV results if requested
if [ -n "$CSV" ]; then
  # Calculating average throughput (with decimal truncated)
  AVERAGE=$(echo "$SUM / $RUNS" | bc)

  echo -n "$NUM_THREADS"
  for t in "${THROUGHPUTS[@]}"; do
      echo -n ",$t"
  done

  echo ",$AVERAGE"
fi
