join-xfrm:
	# jq -s '.' bulk-xfrm/*.json > bulk-xfrm.json
	jq -s 'add' bulk-xfrm/*.json > bulk.json

gro-default:
	jq -s 'add' gro-default/*.json > gro-default.json

plot-gbps:
	../plot-column.py --files bulk.json gro-default.json --x-label "# Flows" \
	--x-key dst_ports --y-key rx_throughput_gibps \
	--y-label "RX Throughput Gbps" --x-log-2 --out dst-ports-gbps.png \
	--title "Average Throughput vs Flows : dst port change"
