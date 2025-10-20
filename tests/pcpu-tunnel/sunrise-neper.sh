#!/bin/bash

set -eu

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number-for-flows-and-threads>"
    exit 1
fi

NUM=$1
RUNS="${RUNS:-5}"
DURATION="${DURATION:-10}"

for i in $(seq 1 ${RUNS}); do
    ./tcp_stream --host 192.1.10.252 --client --num-flows $NUM --num-threads $NUM --source-port 55555 --test-length $DURATION --pin-cpu --nolog > /dev/null
    echo "Run $i done"
done

