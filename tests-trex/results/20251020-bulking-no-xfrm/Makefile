merge:
	jq -s 'add' both-bulk-1.json both-bulk-2.json > both-bulk.json

plot-gbps:
	../plot-column.py --y-key rx_throughput_gibps --files both-bulk.json \
	--files no-bulk.json --title  "Average Forwarded Gbps" \
	--out rx-gbps.png --y-label "RX Throughput Gbps" --x-label "# Flows"

plot-pps:
	../plot-column.py --y-key rx_pps --files both-bulk.json \
	--files no-bulk.json --title  "Average Forwarded Million PPS without IPsec" \
	--out rx-pps.png --y-label "RX MPPS" --x-label "# Flows"
