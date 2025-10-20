#!/bin/bash
set -eu

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number-of-threads>"
    exit 1
fi

NUM_THREADS=$1
SCREEN="${SCREEN:-yes}"
SESSION_NAME="iperf_session"

if [ "$SCREEN" != "0" ] && [ "$SCREEN" != "no" ]; then
    screen -dmS "$SESSION_NAME"
    sleep 0.2  # ensure the session starts
fi

for n in $(seq 1 "${NUM_THREADS}"); do
	port=$((n + 5200))
	CMD="iperf3 -A $n -i 2 -s -p $port"

    	if [ "$SCREEN" != "0" ] && [ "$SCREEN" != "no" ]; then
        	screen -S "$SESSION_NAME" -X screen -t "port_$port" bash -c "$CMD; exec bash"
    else
        bash -c "$CMD"
    fi
done
