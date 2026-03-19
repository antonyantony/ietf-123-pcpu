#!/bin/bash

# Function to process either tcp or udp
process_protocol() {
    local protocol=$1
    local tp=0

    # Print the protocol name at the beginning
    printf "$protocol"

    for f in ${protocol}*.json; do
        tp1=$(jq '.end.sum_sent.bits_per_second' "${f}")

        tp2=$(echo "scale=2; $tp1 / 1024^3" | bc -l)

        tp=$(echo "$tp + $tp2" | bc -l)

        printf ",%0.2f" $tp2
    done

    tp=$(echo "scale=2; $tp / 5" | bc -l)

    # Print the average throughput
    echo ",$tp"
}

# Print the header line once
echo "tcp/udp,#1,#2,#3,#4,#5,avg(5)"

# Call the function for tcp and udp
process_protocol "tcp"
process_protocol "udp"
