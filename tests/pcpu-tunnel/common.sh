# Common gatway init code.
function gateway_init()
{
        # Disable hyperthreading
        echo off | sudo tee /sys/devices/system/cpu/smt/control >/dev/null

        # Insert modified ena driver
        sudo insmod ~/ena_avx-pcpu.ko
        sleep 1

        # Rebind eth0 to ena-avx
        ADDR=$(sudo ethtool -i eth0 | awk '/^bus-info/ {print $2}')
        echo -n "$ADDR" | sudo tee /sys/bus/pci/drivers/ena/unbind >/dev/null
        echo -n "$ADDR" | sudo tee /sys/bus/pci/drivers/ena_avx/bind >/dev/null
        sudo ip link set dev ens5 name eth0
        sudo ip link set dev eth0 up

        # Rebind eth1 to ena-avx
        ADDR=$(sudo ethtool -i eth1 | awk '/^bus-info/ {print $2}')
        echo -n "$ADDR" | sudo tee /sys/bus/pci/drivers/ena/unbind >/dev/null
        echo -n "$ADDR" | sudo tee /sys/bus/pci/drivers/ena_avx/bind >/dev/null
        sudo ip link set dev ens6 name eth1
        sudo ip link set dev eth1 up

        # Just in case it takes a sec for link to be ready
        sleep 1

        # Prep for spi redirection
        sudo ip link set dev eth1 mtu 1380
        sudo ethtool --set-priv-flags eth1 xdp-rx-only on

        echo "Run the following command in another window:"
        echo -e "\tsudo ~/xdp-bench redirect-cpu -v -p spi -q 4096 --cpu-all eth1"
}

# Initialize strongswan.
function strongswan_init()
{
        sudo /usr/sbin/ipsec stop &>/dev/null || true
        sudo cp "${d}/ipsec.secrets" /etc/ipsec.secrets
        sudo cp "${d}/strongswan.conf" /etc/strongswan.conf
        [ -d /etc/swanctl/ ] || mkdir /etc/swanctl/
        sudo cp "${d}/${1}" /etc/swanctl/swanctl.conf
        sudo ~/ip xfrm state flush
        sudo /usr/sbin/ipsec restart
        sleep 2
        sudo swanctl --load-conn
}
