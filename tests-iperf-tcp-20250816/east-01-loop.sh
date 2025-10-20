#!/bin/bash
set -eu

PCPU=${PCPU:-"-baseline"}
duration=${duration:-30}
flows_form=${flows_form:-1}
flows_to=${flows_to:-12}
server=${server:-westb}
black_if=${black_if:-black}

mkdir -p output/
mkdir -p pids
rm -fr pids/* 
rm -f output/tp-table.txt
touch output/tp-table.txt
for j in $(seq "${flows_form}" "${flows_to}"); do 
	rm -f output/iperf3-*.json
	iperf_output="output-iperf-json${PCPU}-${j}"
	rm -fr ${iperf_output}
	mkdir ${iperf_output}
	ip -d -s link show dev $black_if > ${iperf_output}/${j}-ip-link-show-dev-black.txt

	if [ "${PCPU}" != "-baseline" ]; then
		X=$(ip -o x s | wc -l) 
		X1=$(ip x s | grep cpu| wc -l) 
		echo "# before the iperf SAs $X with CPU ID $X1" > ${iperf_output}/${j}-ip-xfrm-state.txt
		ip x s >> ${iperf_output}/${j}-ip-xfrm-state.txt
		echo "# end before the iperf" >> ${iperf_output}/${j}-ip-xfrm-state.txt
		echo "# before the iperf" > ${iperf_output}/${j}-ip-xfrm-policy.txt
		ip x p > ${iperf_output}/${j}-ip-xfrm-policy.txt
		echo "# end before the iperf" >> ${iperf_output}/${j}-ip-xfrm-policy.txt
	fi

	for i in $(seq 1 $j); do
		sport=$((i + 4500))
		dport=$((i + 5200))
		iperf3 -A $i --cport ${sport} -t ${duration} -c $server -p $dport -J > output/iperf3-520${i}.json &
		pid=$!
		echo "$pid" > "pids/iperf3-$pid.pid"
	done

	our_pids=$(cat pids/iperf3-*.pid 2>/dev/null | xargs)
	# Loop while at least one of our PIDs is running
	while : ; do
    		running=0
    		for pid in $our_pids; do
        		if pidof iperf3 | grep -wq "$pid"; then
            			running=1
            			break
        		fi
    		done
    		if [ "$running" -eq 0 ]; then
        		break
    		fi
    		sleep 5
	done

	ag=$(./east.post.sh)
	echo "${j} ${ag}" >> output/tp-table.txt
	echo "${j} ${ag}"
	mv output/*json ${iperf_output}/
	if [ "${PCPU}" != "-baseline" ]; then
		ip x s >> ${iperf_output}/${j}-ip-xfrm-state.txt
		ip x s >> ${iperf_output}/${j}-ip-xfrm-policy.txt
		ip -d -s link show dev ${black_if} >> ${iperf_output}/${j}-ip-link-show-dev-black.txt
	fi
done
