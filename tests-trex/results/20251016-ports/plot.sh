#!/bin/bash
./pps-plot-multi.py --y-key rx_throughput_gibps --files both-bulk.json \
	receiver-bulk.json sender-bulk.json no-bulk.json  --title  "Average Received Gbps" \
	--out rx-gbps.png --y-label "RX Throughput Gbps" --x-label "# Flows"

./pps-plot-multi.py --y-key rx_pps --files both-bulk.json \
	receiver-bulk.json sender-bulk.json no-bulk.json  --title  "Average Received Million PPS" \
	--out rx-mpps.png --y-label "RX PPS" --x-label "# Flows"
