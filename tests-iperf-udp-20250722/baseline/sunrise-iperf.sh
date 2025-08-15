#!/bin/bash

set -eu

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number-for-flows-and-threads>"
    exit 1
fi

NUM_THREADS=$1
RUNS="${RUNS:-1}"
DURATION="${DURATION:-10}"
INTERVAL="${INTERVEL:-2}"  # fix spelling
MTU_UDP_LEN="${MTU_UDP_LEN:-1410}"
SCREEN="${SCREEN:-yes}"
SESSION_NAME="iperf_client"


if [ "$SCREEN" != "0" ] && [ "$SCREEN" != "no" ]; then
    if ! screen -ls | grep -q "\.${SESSION_NAME}"; then
        screen -dmS "$SESSION_NAME"
        sleep 1
    fi
fi

mkdir -p output/
rm -f output/tp-table.txt output/iperf3-*.json

for n in $(seq 1 "${NUM_THREADS}"); do
	port=$((n + 5200))
	cport=$((n + 4500))
	iperf_output="output-iperf-txt-$cport-$port"

	CMD="iperf3 -A $n --cport $cport -i $INTERVAL \
		-c sunset -u -b 2G -t $DURATION -p $port -l $MTU_UDP_LEN"

	if [ "$SCREEN" != "0" ] && [ "$SCREEN" != "no" ]; then
		screen -S "$SESSION_NAME" -X eval "screen -t port_$port bash -c '$CMD; exec bash'"
		echo $CMD
	else
		bash -c "$CMD"
	fi
done
