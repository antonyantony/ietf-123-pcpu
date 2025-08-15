#!/bin/bash
export DURATION=30; 
export RUNS=5;
cd /root/ietf-123-pcpu/tests-iperf-udp/baseline
for i in $(seq 1 8); do 
	./sunrise-iperf-2g.sh $i
	../results/summarize_iperf_loss.py  --input-folder output
done
