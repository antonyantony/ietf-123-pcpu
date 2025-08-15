#!/bin/bash
set -eu

d="$(dirname "$0")"
source "${d}/common.sh"

gateway_init
strongswan_init east.swanctl.conf

# Prep sport mapping for forward plaintext flow
sudo ip link set dev eth0 mtu 1380
sudo ethtool -K eth0 gro off
sudo ethtool --set-priv-flags eth0 xdp-rx-only on
echo "Run the following command in another window:"
echo -e "\tsudo ~/xdp-bench redirect-cpu -v -p l4-sport -q 4096 --cpu-all eth0"
