#!/bin/bash
MTU=1500
UDP="-u"
TP="18G"
RUNS=5
PROTO="tcp"
D=10

do_iperf3 () {
	for i in  $(seq 1 $RUNS); do
		iperf3 -i 2 -c 192.0.2.254 $UDP -b $TP -t ${D} --json > ${PROTO}-${MTU}-${TP}-${i}.json; 
	done
}

for b in $(seq 9 10); do
	TP="${b}G"

	UDP=""
	PROTO=tcp
	do_iperf3

	UDP="-u"
	PROTO=udp
	do_iperf3

done
