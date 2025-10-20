join-xfrm:
	# jq -s '.' bulk-xfrm/*.json > bulk-xfrm.json
	jq -s 'add' bulk-xfrm/*.json > bulk-xfrm.json

gro-default:
	jq -s 'add' gro-default/*.json > gro-default.json

# ../plot-column.py --files bulk.json ../20251016-ports/gro-default.json \

plot-gbps:
	../plot-column.py --files bulk-xfrm.json no-bulk-xfrm.json \
	--x-label "# Flows (log2 scale)" \
	--x-key src_ports --y-key rx_throughput_gibps \
	--y-label "RX Throughput Gbps" --x-log-2 --out dst-ports-gbps.png \
	--title "Average Throughput vs Flows : dst port change"


join-no-bulk:
	jq -s 'add' no-bulk-xfrm/*.json > no-bulk-xfrm.json

