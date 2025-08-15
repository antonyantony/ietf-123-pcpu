#!/bin/bash

DEV=red

RX_BYTES_FILE="/sys/class/net/$DEV/statistics/rx_bytes"
RX_PACKETS_FILE="/sys/class/net/$DEV/statistics/rx_packets"
RX_DROPPED_FILE="/sys/class/net/$DEV/statistics/rx_dropped"
RX_MISSED_FILE="/sys/class/net/$DEV/statistics/rx_missed_errors"
RX_CRC_FILE="/sys/class/net/$DEV/statistics/rx_crc_errors"
RX_ERRORS_FILE="/sys/class/net/$DEV/statistics/rx_errors"
RX_FIFO_FILE="/sys/class/net/$DEV/statistics/rx_fifo_errors"

RX1=$(< "$RX_BYTES_FILE")
P1=$(< "$RX_PACKETS_FILE")
DROP1=$(< "$RX_DROPPED_FILE")
MISS1=$(< "$RX_MISSED_FILE")
CRC1=$(< "$RX_CRC_FILE")
ERR1=$(< "$RX_ERRORS_FILE")
FIFO1=$(< "$RX_FIFO_FILE")

dropped_seen=0
missed_seen=0
crc_seen=0
error_seen=0
fifo_seen=0

while true; do
    sleep 1
    RX2=$(< "$RX_BYTES_FILE")
    P2=$(< "$RX_PACKETS_FILE")
    DROP2=$(< "$RX_DROPPED_FILE")
    MISS2=$(< "$RX_MISSED_FILE")
    CRC2=$(< "$RX_CRC_FILE")
    ERR2=$(< "$RX_ERRORS_FILE")
    FIFO2=$(< "$RX_FIFO_FILE")

    RX_DELTA=$((RX2 - RX1))
    P_DELTA=$((P2 - P1))
    DROP_DELTA=$((DROP2 - DROP1))
    MISS_DELTA=$((MISS2 - MISS1))
    CRC_DELTA=$((CRC2 - CRC1))
    ERR_DELTA=$((ERR2 - ERR1))
    FIFO_DELTA=$((FIFO2 - FIFO1))

    RX_Gbps=$(awk "BEGIN {printf \"%.3f\", (${RX_DELTA}*8)/1e9}")

    if (( P_DELTA > 0 )); then
        RX_Mpps=$(awk "BEGIN {printf \"%.3f\", ${P_DELTA}/1e6}")
    else
        RX_Mpps="0.000"
    fi

    [[ $DROP_DELTA -gt 0 ]] && dropped_seen=1
    [[ $MISS_DELTA -gt 0 ]] && missed_seen=1
    [[ $CRC_DELTA -gt 0 ]] && crc_seen=1
    [[ $ERR_DELTA -gt 0 ]] && error_seen=1
    [[ $FIFO_DELTA -gt 0 ]] && fifo_seen=1

    OUTPUT="RX_Gbps: $RX_Gbps, RX_MPPS: $RX_Mpps"
    if (( missed_seen )); then OUTPUT="$OUTPUT, MISSED: $MISS_DELTA"; fi
    if (( dropped_seen )); then OUTPUT="$OUTPUT, DROPPED: $DROP_DELTA"; fi
    if (( crc_seen )); then OUTPUT="$OUTPUT, CRC_ERRORS: $CRC_DELTA"; fi
    if (( error_seen )); then OUTPUT="$OUTPUT, ERRORS: $ERR_DELTA"; fi
    if (( fifo_seen )); then OUTPUT="$OUTPUT, FIFO_ERRORS: $FIFO_DELTA"; fi

    echo "$OUTPUT"

    RX1=$RX2
    P1=$P2
    DROP1=$DROP2
    MISS1=$MISS2
    CRC1=$CRC2
    ERR1=$ERR2
    FIFO1=$FIFO2
done
