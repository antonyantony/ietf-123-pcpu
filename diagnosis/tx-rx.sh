#!/bin/bash

	R1=$(cat /sys/class/net/red/statistics/rx_bytes);
	T1=$(cat /sys/class/net/red/statistics/tx_bytes);
while true; do
	sleep 1;
	R2=$(cat /sys/class/net/red/statistics/rx_bytes);
	T2=$(cat /sys/class/net/red/statistics/tx_bytes);
	RX=$(( (R2 - R1) * 8 / 1000000000 ));
	TX=$(( (T2 - T1) * 8 / 1000000000 ));
	echo "RX: ${RX} Gbps | TX: ${TX} Gbps";
	R2=${R1}
	T2=${T1}
done
