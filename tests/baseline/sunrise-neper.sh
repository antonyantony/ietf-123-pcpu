#!/bin/bash
set -eu

NPATH=/root/neper/

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number-for-flows-and-threads>"
    exit 1
fi

NUM=$1
RUNS="${RUNS:-5}"
DURATION="${DURATION:-10}"

for i in $(seq 1 ${RUNS}); do
    $NPATH/udp_stream --source-port 4501 --host 10.25.2.1 --client --num-flows $NUM --num-threads $NUM --test-length $DURATION --pin-cpu --nolog > /dev/null
    sleep 2
    echo "Run $i done"
done

