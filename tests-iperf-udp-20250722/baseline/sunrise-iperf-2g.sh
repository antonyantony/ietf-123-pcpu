#!/bin/bash
set -eu

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number-for-flows-and-threads>"
    exit 1
fi

NUM_THREADS=$1
RUNS="${RUNS:-1}"
DURATION="${DURATION:-10}"
MTU_UDP_LEN="${MTU_UDP_LEN:-1410}"
SESSION_NAME="iperf_client"
UDPBW="${UDBW:-2G}"
REMOTE="${REMOTE:-sunset}"

pids=()
mkdir -p output
rm -f output/tp-table.txt output/iperf3-* output/pids/*

for r in $(seq 1 "${RUNS}"); do
	for n in $(seq 1 "${NUM_THREADS}"); do
		port=$((n + 5200))
		cport=$((n + 4500))
		iperf_output="output-iperf-txt-$cport-$port"

		CMD="iperf3 -A $n --cport $cport \
			-c $REMOTE -u -b $UDPBW -t $DURATION -p $port -l $MTU_UDP_LEN"

		# CMD="$CMD -i 0 --logfile output/iperf3-$n-$r-output.txt"
		CMD="$CMD --logfile output/iperf3-$n-$r-output.txt"
		echo "$CMD"
		$CMD &
		PID=$!
		pids+=($PID)  # Store PID in array
	done

	for pid in "${pids[@]}"; do
		if ps -p "$pid" > /dev/null 2>&1; then
			echo "Waiting for PID $pid..."
			wait "$pid"
		fi
	done
	../results/summarize_iperf_loss.py --input-folder output
    	pids=()
done
