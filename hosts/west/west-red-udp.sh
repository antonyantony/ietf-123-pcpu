ethtool -K red  ntuple on
ethtool -N red flow-type udp4  src-port 4500 loc 0 action 0
ethtool -N red flow-type udp4  src-port 4501 loc 1 action 1
ethtool -N red flow-type udp4  src-port 4502 loc 2 action 2
ethtool -N red flow-type udp4  src-port 4503 loc 3 action 3
ethtool -N red flow-type udp4  src-port 4504 loc 4 action 4
ethtool -N red flow-type udp4  src-port 4505 loc 5 action 5
ethtool -N red flow-type udp4  src-port 4506 loc 6 action 6
ethtool -N red flow-type udp4  src-port 4507 loc 7 action 7
ethtool -N red flow-type udp4  src-port 4508 loc 8 action 8
ethtool -N red flow-type udp4  src-port 4509 loc 9 action 9
ethtool -N red flow-type udp4  src-port 4510 loc 10 action 10
ethtool -N red flow-type udp4  src-port 4511 loc 11 action 11
ethtool -N red flow-type udp4  src-port 4512 loc 12 action 12
ethtool -N red flow-type udp4  src-port 4513 loc 13 action 13
ethtool -N red flow-type udp4  src-port 4514 loc 14 action 14
ethtool -N red flow-type udp4  src-port 4515 loc 15 action 15
ethtool -N red flow-type udp4  dst-port 1 loc 15 action 1
# ethtool -n red
