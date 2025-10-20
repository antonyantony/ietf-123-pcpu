sysctl -w net.ipv4.conf.all.send_redirects=0
sysctl -w net.ipv4.conf.all.rp_filter=0
sysctl -w net.ipv4.conf.default.rp_filter=0
sysctl -w net.core.rmem_max=268435456
sysctl -w net.core.wmem_max=268435456
sysctl -w net.core.rmem_default=134217728
sysctl -w net.core.wmem_default=134217728
sysctl -w net.core.netdev_max_backlog=100000

ethtool -L red combined 16
ethtool -L black combined 16

while true; do   RX1=$(cat /sys/class/net/red/statistics/rx_bytes);   DROP1=$(cat /sys/class/net/red/statistics/rx_dropped);   MISS1=$(cat /sys/class/net/red/statistics/rx_missed_errors);   sleep 1;   RX2=$(cat /sys/class/net/red/statistics/rx_bytes);   DROP2=$(cat /sys/class/net/red/statistics/rx_dropped);   MISS2=$(cat /sys/class/net/red/statistics/rx_missed_errors);    RX_RATE=$(( (RX2 - RX1) * 8 / 1000000000 ));   DROP_DELTA=$((DROP2 - DROP1));   MISS_DELTA=$((MISS2 - MISS1));    echo "RX: ${RX_RATE} Gbps | Dropped: ${DROP_DELTA} | Missed: ${MISS_DELTA}"; done

while true; do   R1=$(cat /sys/class/net/red/statistics/rx_bytes);   T1=$(cat /sys/class/net/red/statistics/tx_bytes);   sleep 1;   R2=$(cat /sys/class/net/red/statistics/rx_bytes);   T2=$(cat /sys/class/net/red/statistics/tx_bytes);   RX=$(( (R2 - R1) * 8 / 1000000000 ));   TX=$(( (T2 - T1) * 8 / 1000000000 ));   echo "RX: ${RX} Gbps | TX: ${TX} Gbps"; done

