ip netns add east
ip link set redeast netns east
ip netns exec east ip link set up redeast
ip netns exec east ip addr add 192.0.2.252/24 dev redeast
ip netns exec east ip route add 192.0.1.0/24 via 192.0.2.254
